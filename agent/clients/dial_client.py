import json
import logging
import re
from collections import defaultdict
from typing import Any, AsyncGenerator

from openai import AsyncAzureOpenAI

from agent.clients.stdio_mcp_client import StdioMCPClient
from agent.models.message import Message, Role
from agent.clients.http_mcp_client import HttpMCPClient

logger = logging.getLogger(__name__)


class PIIFilter:
    """Filter for detecting and removing credit card numbers from text"""
    
    # Regex patterns for major credit card types
    CREDIT_CARD_PATTERNS = [
        # Visa (starts with 4, 13-16 digits)
        r'\b4[0-9]{12}(?:[0-9]{3})?\b',
        # MasterCard (starts with 51-55 or 2221-2720, 16 digits)
        r'\b5[1-5][0-9]{14}\b',
        r'\b(?:222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}\b',
        # American Express (starts with 34 or 37, 15 digits)
        r'\b3[47][0-9]{13}\b',
        # Discover (starts with 6011 or 65, 16 digits)
        r'\b6011[0-9]{12}\b',
        r'\b65[0-9]{14}\b',
        # Generic pattern for formatted cards (XXXX-XXXX-XXXX-XXXX or XXXX XXXX XXXX XXXX)
        r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
    ]
    
    @classmethod
    def filter_credit_cards(cls, text: str) -> str:
        """Remove credit card numbers from text"""
        if not text:
            return text
            
        filtered_text = text
        for pattern in cls.CREDIT_CARD_PATTERNS:
            filtered_text = re.sub(pattern, '[CREDIT-CARD-REDACTED]', filtered_text)
        
        return filtered_text


class DialClient:
    """Handles AI model interactions and integrates with MCP client"""

    def __init__(
            self,
            api_key: str,
            endpoint: str,
            model: str,
            tools: list[dict[str, Any]],
            tool_name_client_map: dict[str, HttpMCPClient | StdioMCPClient]
    ):
        self.tools = tools
        self.tool_name_client_map = tool_name_client_map
        self.model = model
        self.async_openai = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=""
        )
        logger.info(
            "DialClient initialized",
            extra={
                "model": model,
                "endpoint": endpoint,
                "tool_count": len(tools)
            }
        )

    async def response(self, messages: list[Message]) -> Message:
        """Non-streaming completion with tool calling support"""
        logger.debug(
            "Creating non-streaming completion",
            extra={"message_count": len(messages), "model": self.model}
        )

        response = await self.async_openai.chat.completions.create(
            model=self.model,
            messages=[msg.to_dict() for msg in messages],
            tools=self.tools,
            temperature=0.0,
            stream=False
        )

        content = response.choices[0].message.content or ""
        # Filter credit card numbers for PII protection
        filtered_content = PIIFilter.filter_credit_cards(content)
        
        ai_message = Message(
            role=Role.ASSISTANT,
            content=filtered_content,
        )
        if tool_calls := response.choices[0].message.tool_calls:
            ai_message.tool_calls = tool_calls
            logger.info(
                "AI response includes tool calls",
                extra={"tool_call_count": len(tool_calls)}
            )

        if ai_message.tool_calls:
            messages.append(ai_message)
            await self._call_tools(ai_message, messages)
            return await self.response(messages)

        logger.debug("Non-streaming completion finished")
        return ai_message

    async def stream_response(self, messages: list[Message]) -> AsyncGenerator[str, None]:
        """
        Streaming completion with tool calling support.
        Yields SSE-formatted chunks.
        """
        logger.debug(
            "Creating streaming completion",
            extra={"message_count": len(messages), "model": self.model}
        )

        stream = await self.async_openai.chat.completions.create(
            model=self.model,
            messages=[msg.to_dict() for msg in messages],
            tools=self.tools,
            temperature=0.0,
            stream=True
        )

        content_buffer = ""
        tool_deltas = []

        async for chunk in stream:
            delta = chunk.choices[0].delta

            if delta and delta.content:
                # Filter credit card numbers in real-time
                filtered_content = PIIFilter.filter_credit_cards(delta.content)
                
                chunk_data = {
                    "choices": [
                        {"delta": {"content": filtered_content}, "index": 0, "finish_reason": None}
                    ]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                content_buffer += filtered_content

            if delta.tool_calls:
                tool_deltas.extend(delta.tool_calls)

        if tool_deltas:
            tool_calls = self._collect_tool_calls(tool_deltas)
            ai_message = Message(
                role=Role.ASSISTANT,
                content=content_buffer,
                tool_calls=tool_calls
            )
            messages.append(ai_message)
            await self._call_tools(ai_message, messages)

            logger.info(
                "Recursively streaming after tool calls",
                extra={"tool_call_count": len(tool_calls)}
            )

            async for chunk in self.stream_response(messages):
                yield chunk
            return

        messages.append(Message(role=Role.ASSISTANT, content=content_buffer))

        final_chunk = {
            "choices": [
                {"delta": {}, "index": 0, "finish_reason": "stop"}
            ]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"

        logger.debug("Streaming completed")

    def _collect_tool_calls(self, tool_deltas):
        """Convert streaming tool call deltas to complete tool calls"""
        tool_dict = defaultdict(
            lambda: {
                "id": None,
                "function": {"arguments": "", "name": None},
                "type": None
            }
        )

        for delta in tool_deltas:
            idx = delta.index
            if delta.id:
                tool_dict[idx]["id"] = delta.id
            if delta.function and delta.function.name:
                tool_dict[idx]["function"]["name"] = delta.function.name
            if delta.function and delta.function.arguments:
                tool_dict[idx]["function"]["arguments"] += delta.function.arguments
            if delta.type:
                tool_dict[idx]["type"] = delta.type

        logger.debug(
            "Collected tool calls from deltas",
            extra={"tool_call_count": len(tool_dict)}
        )

        return list(tool_dict.values())

    async def _call_tools(self, ai_message: Message, messages: list[Message], silent: bool = False):
        """Execute tool calls using MCP client"""
        logger.info(
            "Executing tool calls",
            extra={"tool_call_count": len(ai_message.tool_calls)}
        )

        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            logger.debug(
                "Processing tool call",
                extra={"tool_name": tool_name, "tool_args": tool_args}
            )

            mcp_client = self.tool_name_client_map.get(tool_name)
            if not mcp_client:
                error_msg = f"Tool '{tool_name}' not found in available tools"
                logger.warning(error_msg, extra={"tool_name": tool_name})
                tool_message = Message(
                    role=Role.TOOL,
                    content=error_msg,
                    tool_call_id=tool_call["id"]
                )
                messages.append(tool_message)
                continue

            try:
                tool_result = await mcp_client.call_tool(tool_name, tool_args)
                logger.info(
                    "Tool executed successfully",
                    extra={
                        "tool_name": tool_name,
                        "result_length": len(str(tool_result))
                    }
                )
            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                logger.error(
                    error_msg,
                    extra={"tool_name": tool_name, "error": str(e)}
                )
                tool_result = error_msg

            tool_message = Message(
                role=Role.TOOL,
                content=str(tool_result),
                tool_call_id=tool_call["id"]
            )
            messages.append(tool_message)

        logger.debug("All tool calls processed")
