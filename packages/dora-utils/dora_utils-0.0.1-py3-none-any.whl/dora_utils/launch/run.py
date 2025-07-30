import atexit
import shutil
import subprocess
import tempfile
from pathlib import Path

from omegaconf import DictConfig, OmegaConf


def write_tmp(subcfg: DictConfig, tmp_dir: Path, name: str) -> Path:
    """Write a temporary yaml file for the given subconfig."""
    yaml_data = OmegaConf.to_yaml(subcfg, resolve=True)
    yaml_path = tmp_dir / f"{name}.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_data)
    return yaml_path


def run(cfg: DictConfig) -> None:
    """Main function to run the judo stack."""
    tmp_dir = Path(tempfile.mkdtemp())

    # [HACK] instantiate dora nodes specified in the hydra config
    # we extract each node config and write it to a temp yaml file, then use dora to launch the node using Popen.
    # there were strange interactions when trying to spin the nodes by manually calling spin with threading or mp, but
    # this workaround seems to work with dynamic nodes.
    dataflow_path = write_tmp(cfg.dataflow, tmp_dir, "tmp_dataflow")
    process = subprocess.Popen(f"dora up && dora start {dataflow_path}", shell=True)

    yaml_paths = []
    for node_cfg in cfg.node_definitions.values():
        # allow skipping of node definitions by setting to null when overriding configs
        if node_cfg is None:
            continue

        node_name = f"tmp_{node_cfg.node_id}"
        yaml_path = write_tmp(node_cfg, tmp_dir, node_name)
        subprocess.Popen(f"python {Path(__file__).parent}/_launch_node.py -cp {tmp_dir} -cn {node_name}", shell=True)
        yaml_paths.append(yaml_path)

    # register a cleanup function to remove the temp yaml files when the script exits
    def _cleanup_tmp_dir():
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass

    atexit.register(_cleanup_tmp_dir)

    # don't terminate the script until the main dora process does
    process.wait()
