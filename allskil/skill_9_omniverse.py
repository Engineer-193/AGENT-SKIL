import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WORK_DIR

SKILL_NAME = "NVIDIA Omniverse"
SKILL_DESC = "NVIDIA Omniverse platform for 3D simulation, USD workflows, digital twins, and collaborative real-time rendering"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "omniverse_setup",
            "description": "Set up NVIDIA Omniverse Kit SDK or Replicator for simulation",
            "parameters": {
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["kit-sdk", "replicator", "isaac-sim", "usd-composer", "farm"],
                        "description": "Omniverse component to set up"
                    },
                    "version": {"type": "string", "description": "Version tag, default 'latest'", "default": "latest"}
                },
                "required": ["component"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "omniverse_replicator_generate",
            "description": "Generate synthetic training data using NVIDIA Omniverse Replicator",
            "parameters": {
                "type": "object",
                "properties": {
                    "scene_description": {"type": "string", "description": "Description of the scene to generate"},
                    "num_frames": {"type": "integer", "description": "Number of frames/images to generate", "default": 1000},
                    "output_format": {
                        "type": "string",
                        "enum": ["rgb", "depth", "segmentation", "bounding_box", "all"],
                        "description": "Output data format"
                    },
                    "output_dir": {"type": "string", "description": "Output directory for generated data"}
                },
                "required": ["scene_description", "output_dir"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "omniverse_usd_create",
            "description": "Create or modify a USD (Universal Scene Description) file",
            "parameters": {
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string", "description": "Name of the USD scene"},
                    "objects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Objects to add to scene, e.g. ['cube', 'sphere', 'robot_arm']"
                    },
                    "output_path": {"type": "string", "description": "Output .usd or .usda file path"}
                },
                "required": ["scene_name", "output_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "omniverse_digital_twin",
            "description": "Set up a digital twin workflow using Omniverse for a facility or robot",
            "parameters": {
                "type": "object",
                "properties": {
                    "asset_type": {
                        "type": "string",
                        "enum": ["factory", "warehouse", "robot", "vehicle", "building", "city"],
                        "description": "Type of asset to create digital twin for"
                    },
                    "description": {"type": "string", "description": "Description of the real-world asset"},
                    "data_source": {"type": "string", "description": "Source of real-world data: 'lidar', 'cad', 'photogrammetry', 'manual'"}
                },
                "required": ["asset_type", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "omniverse_rtx_render",
            "description": "Set up RTX path-tracing render job in Omniverse Farm",
            "parameters": {
                "type": "object",
                "properties": {
                    "usd_file": {"type": "string", "description": "Path to USD scene file"},
                    "renderer": {
                        "type": "string",
                        "enum": ["rtx-realtime", "rtx-pathtracing", "iray"],
                        "description": "Renderer to use"
                    },
                    "resolution": {"type": "string", "description": "Output resolution, e.g. '1920x1080'", "default": "1920x1080"},
                    "frames": {"type": "string", "description": "Frame range, e.g. '1-100'", "default": "1"}
                },
                "required": ["usd_file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "omniverse_isaac_sim",
            "description": "Run Isaac Sim robot simulation for training robot policies",
            "parameters": {
                "type": "object",
                "properties": {
                    "robot": {"type": "string", "description": "Robot model name, e.g. 'franka', 'carter', 'spot', 'humanoid'"},
                    "task": {"type": "string", "description": "Task to simulate, e.g. 'pick_place', 'navigation', 'manipulation'"},
                    "physics_engine": {
                        "type": "string",
                        "enum": ["physx", "flex"],
                        "description": "Physics engine to use",
                        "default": "physx"
                    },
                    "headless": {"type": "boolean", "description": "Run in headless mode (no display)", "default": True}
                },
                "required": ["robot", "task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "omniverse_explain",
            "description": "Explain NVIDIA Omniverse components and use cases",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["overview", "usd", "replicator", "isaac_sim", "digital_twin", "kit_sdk"],
                        "description": "Topic to explain"
                    }
                },
                "required": ["topic"]
            }
        }
    }
]


def omniverse_setup(component: str, version: str = "latest") -> str:
    setups = {
        "kit-sdk": (
            "📦 **Omniverse Kit SDK Setup:**\n```bash\n"
            "pip install omniverse-kit\n# Or download from:\n"
            "# https://developer.nvidia.com/omniverse/get-started\n```"
        ),
        "replicator": (
            "🔁 **Omniverse Replicator Setup:**\n```bash\n"
            "pip install omni-replicator-core\n"
            "# Or in Isaac Sim: already included\n# import omni.replicator.core as rep\n```"
        ),
        "isaac-sim": (
            "🤖 **Isaac Sim Setup (Docker):**\n```bash\n"
            f"docker pull nvcr.io/nvidia/isaac-sim:{version}\n"
            "docker run --gpus all -e ACCEPT_EULA=Y \\\n"
            "  --rm -it nvcr.io/nvidia/isaac-sim:latest\n```\n"
            "Or download Isaac Sim via Omniverse Launcher."
        ),
        "usd-composer": (
            "🎨 **USD Composer:** Download via Omniverse Launcher\n"
            "https://www.nvidia.com/en-us/omniverse/apps/composer/"
        ),
        "farm": (
            "🌾 **Omniverse Farm Queue Setup:**\n```bash\n"
            "pip install omni-farm-client\n"
            "# Start Farm Queue: omni.farm.queue --config farm_config.toml\n```"
        )
    }
    return setups.get(component, f"Setup info for {component}: https://docs.omniverse.nvidia.com/")


def omniverse_replicator_generate(scene_description: str, output_dir: str, num_frames: int = 1000, output_format: str = "all") -> str:
    os.makedirs(output_dir, exist_ok=True)
    return (
        f"🔁 **Omniverse Replicator — Synthetic Data Generation**\n"
        f"Scene: `{scene_description}`\n"
        f"Frames: {num_frames} | Format: {output_format} | Output: `{output_dir}`\n\n"
        f"```python\nimport omni.replicator.core as rep\n\n"
        f"with rep.new_layer():\n"
        f"    # Scene: {scene_description}\n"
        f"    plane = rep.create.plane(scale=10)\n"
        f"    objects = rep.create.from_usd(\n"
        f"        rep.utils.get_usd_files('./assets', recursive=True)\n"
        f"    )\n\n"
        f"    camera = rep.create.camera(position=(0, 3, 3), look_at=(0, 0, 0))\n"
        f"    render_product = rep.create.render_product(camera, (1920, 1080))\n\n"
        f"    with rep.randomizer.register(rep.randomize.scatter_2d(plane)):\n"
        f"        rep.modify.pose(objects, rotation=rep.distribution.uniform((0,0,-90),(0,0,90)))\n\n"
        f"    writer = rep.WriterRegistry.get('BasicWriter')\n"
        f"    writer.initialize(\n"
        f"        output_dir='{output_dir}',\n"
        f"        rgb={'rgb' in output_format or output_format == 'all'},\n"
        f"        distance_to_image_plane={'depth' in output_format or output_format == 'all'},\n"
        f"        bounding_box_2d_tight={'bounding_box' in output_format or output_format == 'all'},\n"
        f"        semantic_segmentation={'segmentation' in output_format or output_format == 'all'},\n"
        f"    )\n"
        f"    writer.attach(render_product)\n\n"
        f"rep.orchestrator.run_until_complete(num_frames={num_frames})\n"
        f"print(f'Generated {num_frames} frames in {output_dir}')\n```"
    )


def omniverse_usd_create(scene_name: str, output_path: str, objects: list = None) -> str:
    objects = objects or ["cube"]
    obj_code = "\n".join([
        f"    {obj}_prim = UsdGeom.Cube(stage.DefinePrim(f'/World/{obj}', 'Cube'))"
        for obj in objects
    ])
    return (
        f"📐 **USD Scene: {scene_name}**\n"
        f"Objects: {', '.join(objects)} | Output: `{output_path}`\n\n"
        f"```python\nfrom pxr import Usd, UsdGeom, Gf\n\n"
        f"stage = Usd.Stage.CreateNew('{output_path}')\n"
        f"UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)\n\n"
        f"world = UsdGeom.Xform.Define(stage, '/World')\n"
        f"{obj_code}\n\n"
        f"stage.SetDefaultPrim(stage.GetPrimAtPath('/World'))\n"
        f"stage.Save()\nprint(f'USD scene saved: {output_path}')\n```\n\n"
        f"Open in USD Composer: `File > Open > {output_path}`"
    )


def omniverse_digital_twin(asset_type: str, description: str, data_source: str = "manual") -> str:
    return (
        f"🏭 **Digital Twin: {asset_type.title()}**\n"
        f"Asset: {description}\n"
        f"Data source: {data_source}\n\n"
        f"**Workflow:**\n"
        f"1. **Capture** — {data_source} scan of `{description}`\n"
        f"2. **Import** — Bring CAD/point cloud into Omniverse USD Composer\n"
        f"3. **Enrich** — Add sensors, physics, materials in USD\n"
        f"4. **Simulate** — Run real-time physics with PhysX\n"
        f"5. **Connect** — Live sync with IoT/PLM via Omniverse Connectors\n\n"
        f"```bash\n# Start Omniverse Nucleus (asset server)\ndocker run -p 3009:3009 -p 3019:3019 \\\n"
        f"  nvcr.io/nvidia/omniverse/nucleus:latest\n```\n\n"
        f"Connectors available for: Revit, SolidWorks, Unreal Engine, Blender, Rhino"
    )


def omniverse_rtx_render(usd_file: str, renderer: str = "rtx-pathtracing", resolution: str = "1920x1080", frames: str = "1") -> str:
    w, h = resolution.split("x") if "x" in resolution else ("1920", "1080")
    return (
        f"🎬 **Omniverse RTX Render**\n"
        f"File: `{usd_file}` | Renderer: `{renderer}` | Res: {resolution} | Frames: {frames}\n\n"
        f"```bash\n# Via Kit CLI\n"
        f"./kit/kit ./apps/omni.create.sh \\\n"
        f"  --/renderer/enabled='{renderer}' \\\n"
        f"  --/app/auto_load_usd='{usd_file}' \\\n"
        f"  --/exts/omni.services.renderer.async/port=8011 \\\n"
        f"  --no-window\n```\n\n"
        f"Or via Farm:\n```bash\nomni-farm-client submit \\\n"
        f"  --usd {usd_file} \\\n"
        f"  --renderer {renderer} \\\n"
        f"  --resolution {w} {h} \\\n"
        f"  --frames {frames}\n```"
    )


def omniverse_isaac_sim(robot: str, task: str, physics_engine: str = "physx", headless: bool = True) -> str:
    headless_flag = "--headless" if headless else ""
    return (
        f"🤖 **Isaac Sim: {robot} — {task}**\n"
        f"Physics: `{physics_engine}` | Headless: {headless}\n\n"
        f"```bash\n"
        f"./python.sh standalone_examples/api/omni.isaac.franka/{task}.py {headless_flag}\n```\n\n"
        f"```python\nfrom omni.isaac.kit import SimulationApp\napp = SimulationApp({{'headless': {str(headless).lower()}}})\n\n"
        f"from omni.isaac.core import World\nfrom omni.isaac.{robot} import {robot.title()}\n\n"
        f"world = World(physics_dt=1/60.0)\nrobot = world.scene.add({robot.title()}(prim_path='/World/robot'))\n\n"
        f"world.reset()\nfor i in range(1000):\n"
        f"    # {task} control loop\n"
        f"    world.step(render=not {str(headless).lower()})\n\n"
        f"app.close()\n```\n\n"
        f"Prebuilt tasks: pick_place, follow_target, stacking, navigation"
    )


def omniverse_explain(topic: str) -> str:
    explanations = {
        "overview": (
            "🌐 **NVIDIA Omniverse Overview**\n\n"
            "Open platform for 3D design collaboration and simulation:\n"
            "• **USD** — Universal Scene Description (Pixar/NVIDIA open standard)\n"
            "• **RTX Rendering** — Photorealistic real-time ray tracing\n"
            "• **Physics** — PhysX 5 simulation\n"
            "• **Replicator** — Synthetic data generation for AI training\n"
            "• **Isaac Sim** — Robot simulation and training\n"
            "Docs: https://docs.omniverse.nvidia.com/"
        ),
        "usd": "📐 USD (Universal Scene Description) is the open 3D file format used across Omniverse — supports layering, instancing, and live collaboration.",
        "replicator": "🔁 Replicator generates unlimited synthetic training data (images, depth, segmentation, bounding boxes) for computer vision AI training.",
        "isaac_sim": "🤖 Isaac Sim is a GPU-accelerated robot simulator built on Omniverse — run thousands of parallel simulations for RL/IL training.",
        "digital_twin": "🏭 Digital Twins mirror real-world facilities/robots in Omniverse — connect IoT sensors for live monitoring and predictive simulation.",
        "kit_sdk": "🛠️ Omniverse Kit SDK lets developers build custom apps and extensions on top of Omniverse's USD, rendering, and physics stack."
    }
    return explanations.get(topic, f"Unknown topic: {topic}")


TOOL_HANDLERS = {
    "omniverse_setup": omniverse_setup,
    "omniverse_replicator_generate": omniverse_replicator_generate,
    "omniverse_usd_create": omniverse_usd_create,
    "omniverse_digital_twin": omniverse_digital_twin,
    "omniverse_rtx_render": omniverse_rtx_render,
    "omniverse_isaac_sim": omniverse_isaac_sim,
    "omniverse_explain": omniverse_explain,
}
