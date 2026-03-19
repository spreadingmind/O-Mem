#!/usr/bin/env python
# coding=utf-8
# Copyright 2025 The OPPO Personal AI team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import re
import json

def ensure_directory_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def extract_json_from_llm_output(text: str) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("Empty response from LLM")

    # 1. Try fenced code blocks (robust)
    code_blocks = re.findall(r"```(?:json|JSON)?\s*([\s\S]*?)\s*```", text)
    for block in code_blocks:
        try:
            return json.loads(block)
        except Exception:
            pass

    # 2. Try to extract JSON object using bracket balancing
    json_candidate = _extract_first_json_object(text)
    if json_candidate:
        try:
            return json.loads(json_candidate)
        except Exception:
            # try to repair
            repaired = _repair_json(json_candidate)
            try:
                return json.loads(repaired)
            except Exception:
                pass

    # 3. Last attempt: full text
    try:
        print(text)
        return json.loads(text)
    except Exception:
        repaired = _repair_json(text)
        return json.loads(repaired)


def _extract_first_json_object(text: str) -> str | None:
    stack = 0
    start = None

    for i, char in enumerate(text):
        if char == '{':
            if stack == 0:
                start = i
            stack += 1
        elif char == '}':
            stack -= 1
            if stack == 0 and start is not None:
                return text[start:i + 1]

    return None


def _repair_json(s: str) -> str:
    s = s.strip()
    s = re.sub(r",\s*([}\]])", r"\1", s)
    if "'" in s and '"' not in s:
        s = s.replace("'", '"')

    return s