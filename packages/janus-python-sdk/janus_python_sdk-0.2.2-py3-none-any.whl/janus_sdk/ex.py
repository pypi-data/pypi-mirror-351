#!/usr/bin/env python3
"""
Clean Janus SDK Example

This example demonstrates the simplified Janus SDK with automatic tracing.
The SDK now handles all OpenTelemetry setup automatically!

Key Features:
- ✅ Automatic tracing initialization
- ✅ Built-in @track decorator
- ✅ Progress bar enabled by default
- ✅ Zero manual setup required
"""

import asyncio
import json
from openai import AsyncOpenAI

# Import the clean Janus SDK
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from __init__ import run_simulations, track

# Math functions with automatic conversation context tracking
@track
def add(x: int, y: int) -> int:
    """Add two numbers together."""
    return x + y

@track
def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y

@track
def divide(x: float, y: float) -> float:
    """Divide two numbers."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

# Tool definitions for OpenAI
math_tools = [
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "Divide two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
        },
    },
]

tools_map = {
    "add": add,
    "multiply": multiply,
    "divide": divide,
}

class MathAgent:
    """
    Simple Math Agent that automatically gets conversation context.
    
    The Janus SDK automatically handles all tracing setup!
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key="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")
        self.system_prompt = "You are a helpful math assistant. Use the provided tools to perform calculations when needed. Always show your work and explain your reasoning."
    
    async def runner(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=math_tools,
            tool_choice="auto",
        )

        # Handle tool calls
        while response.choices[0].finish_reason != "stop":
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = tools_map[function_name]
                    function_args = json.loads(tool_call.function.arguments)

                    try:
                        # This automatically gets conversation context from the SDK!
                        function_response = function_to_call(**function_args)
                        function_response_json = json.dumps(function_response)
                    except Exception as e:
                        function_response_json = json.dumps({"error": str(e)})

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response_json,
                    })

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=math_tools,
            )

        return response.choices[0].message.content

async def main():
    # The SDK automatically initializes tracing and shows progress bar!
    results = await run_simulations(
        num_simulations=2,
        max_turns=3,
        target_agent=lambda: MathAgent().runner,
        api_key="sk-ad41d1ca98ab4cef8df1c779257abe3d",
    )
    
    print("\n✅ Simulation completed!")
    print(f"📊 Ran {len(results)} simulations")
    print("🔍 Check your Janus dashboard for traces and results!")
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 