#!/bin/bash

echo '{"person":{"name":"John", "age":30, "city":"New York"}}' | jq '.person.name'