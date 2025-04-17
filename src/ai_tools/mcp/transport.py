import json
import uuid
import datetime

class MCPMessage:
    def __init__(self, role, content, context=None, msg_id=None, timestamp=None):
        self.id = msg_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.datetime.utcnow().isoformat()
        self.role = role  # e.g., "user", "assistant", "system"
        self.content = content
        self.context = context or {}

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "role": self.role,
            "content": self.content,
            "context": self.context
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return MCPMessage(
            role=data["role"],
            content=data["content"],
            context=data.get("context"),
            msg_id=data["id"],
            timestamp=data["timestamp"]
        )


# Example Usage
if __name__ == "__main__":
    # Creating a message
    msg = MCPMessage(
        role="user",
        content="Generate Python code for a REST API.",
        context={"language": "Python", "framework": "FastAPI"}
    )

    # Serialize to JSON
    json_output = msg.to_json()
    print("Serialized MCP Message:\n", json_output)

    # Deserialize from JSON
    parsed = MCPMessage.from_json(json_output)
    print("\nDeserialized Message Object:\n", parsed.to_dict())
