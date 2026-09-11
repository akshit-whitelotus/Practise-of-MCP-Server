import asyncio

from mcp import Client


MCP_URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    async with Client(MCP_URL) as client:

        print("Connected to MCP server")

        # -------------------------
        # Tools
        # -------------------------

        tools_result = await client.list_tools()

        print("\nAvailable Tools:")

        for tool in tools_result.tools:
            print(f"- {tool.name}")
            print(f"  Description: {tool.description}")

        print("\nCalling add_numbers...")

        result = await client.call_tool(
            "add_numbers",
            {
                "a": 10,
                "b": 5,
            },
        )

        print(
            "add_numbers: ",
            result.structured_content["result"],
        )

        print("\nCalling substract_numbers...")

        result = await client.call_tool(
            "substract_numbers",
            {
                "a": 10,
                "b": 5,
            },
        )

        print(
            "substract_numbers: ",
            result.structured_content["result"],
        )

        print("\nCalling multiply_numbers...")

        result = await client.call_tool(
            "multiply_numbers",
            {
                "a": 10,
                "b": 5,
            },
        )

        print(
            "multiply_numbers: ",
            result.structured_content["result"],
        )
        print("\nCreating Student...")

        result=await client.call_tool(
            "create_student_tool",
            {
                "student_id":"1",
                "name":"Akshit Thakkar",
                "email":"akshit@example.com",
                "role":"Backend Developer",

            }
        )

        print("Created:",result)

        print("\nGetting student...")

        result=await client.call_tool(
            "get_student_tool",
            {
                "student_id":"1"
            }
        )

        print("Student:",result)

        print("\nListing Students....")

        result=await client.call_tool(
            "list_students_tool",
            {}
        )

        print("Students: ",result)

        print("\nDeleting student....")

        result=await client.call_tool(
            "delete_student_tool",
            {
                "student_id":"1"
            }
        )

        print("Deleted:", result)

        # -------------------------
        # Resources
        # -------------------------

        print("\nAvailable Resources....")

        resources = await client.list_resources()

        for resource in resources.resources:
            print(f"- {resource.uri}")
            print(f"- Name: {resource.name}")

        print("\nReading student resources...")

        result = await client.read_resource(
            "students://list"
        )

        print(result)

        print("\nGetting non-existing student...")

        result = await client.call_tool(
            "get_student_tool",
            {
                "student_id": "999",
            },
        )

        print("Result:", result)

        # -------------------------
        # Prompts
        # -------------------------

        print("\nAvailable Prompts....")

        prompts = await client.list_prompts()

        for prompt in prompts.prompts:
            print(f"- {prompt.name}")
            print(f"- Description: {prompt.description}")

        print("\nGetting Student analysis prompt...")

        result = await client.get_prompt(
            "student_analysis",
            {
                "student_name": "Akshit Thakkar",
            },
        )

        print(result)

        print("\nSearching project code....")

        result= await client.call_tool(
            "search_code_tool",
            {
                "query":"FastAPI"
            }
        )
        print("Search Results:")
        print(result.content[0].text)

        print("\n Git repository status....")
        result = await client.call_tool(
            "get_git_status_tool",
            {},
        )
        print(result.content[0].text)    

        print("\n Git Diff....")
        result = await client.call_tool(
            "get_git_diff_tool",
            {},
        )
        print(result.content[0].text)

        print("\nReading app/server.py....")
        result = await client.call_tool(
            "read_file_tool",
            {
                "file_path":"app/server.py"
            }
        )
        print(result.content[0].text)

        print("\nProject Health....")

        result = await client.call_tool(
            "project_health_tool",
            {},
        )

        print(result.content[0].text)
if __name__ == "__main__":
    asyncio.run(main())