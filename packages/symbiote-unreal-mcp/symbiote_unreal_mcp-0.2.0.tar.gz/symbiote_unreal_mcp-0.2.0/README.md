# Symbiote UE5 Plugin

An UE5 plugin, that integrates MCP and a handful of custom functions into Unreal Engine Editor.

## Installation

#### Prerequesites (for Windows)

1. Unreal Engine 5.5
2. Visual Studio 2019/2022 (for platform other than Win, use appropriate equivalent)
3. Python (Im not sure which version - gonna have to check that out)

#### Steps:

1. Create an Unreal project if you don't have one yet.
2. Git clone this repo into your project **"/Plugins"** folder. (create one if it doesn't exist)
   > Result after cloning should look like **".../MyProject/Plugins/Symbiote_UE5"**
3. Right click on your .uproject file and pick **"Generate Visual Studio Project Files"**
4. Once created, open the **.sln**, and **Build** your game with **Developement Editor** and **Win64** in solution configuration (two dropdown selects in the top bar)

Alright! If everything went smoothly, you got yourself a Symbiote plugin, that's ready to roll. Now let's just tell Claude where to find it.

1. If you know where your **"claude_desktop_config.json"** is, you can jump to point **3**
2. Open **Claude** and in the top-left corner open the Menu and go to **"File/Settings""** Then in **Developer** section choose **Edit config**. It should point you to the correct file.
3. Open the file in the editor of your choosing, and add an **unrealMCP** object into the **mcpServers** along with some parameters. Assuming you had a completely empty config, the final result should look like this:

```
{
	"mcpServers": {
		"unrealMCP": {
			"command": "python",
			"args": [
				"{path to your project}/Plugins/Symbiote_UE5/Resources/Python/unreal_mcp_server.py"
			]
		}
	}
}
```

> This basically tells Claude to run **python unreal_mcp_server.py**.

4. Save the file, **restart Claude** and you're good to go.

## Using

1. Open your Unreal project
2. Start Claude
3. Check available tools below the chat input and give it a go :)

> I left all of the original MCP functions alive, so there's a bunch of cool features to try.
