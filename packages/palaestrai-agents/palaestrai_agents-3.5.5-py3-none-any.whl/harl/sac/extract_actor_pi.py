from typing import Tuple

import argparse
from pathlib import Path

import numpy
import numpy as np
import torch

from harl.sac.network import Actor, SquashedGaussianMLPActor


def get_pi(model_path: str) -> SquashedGaussianMLPActor:
    model: Actor = torch.load(
        model_path, map_location=torch.device("cpu"), weights_only=False
    )  # type: ignore[annotation-unchecked]
    pi = model.pi  # type: ignore[annotation-unchecked]
    assert isinstance(pi, SquashedGaussianMLPActor)

    return pi


def get_dest_file_path(model_path: Path, ending: str) -> str:
    suffix = "".join(model_path.suffixes)
    new_suffix = suffix.replace(".", "_")
    file_path = str(model_path).replace(suffix, new_suffix) + ending

    return file_path


def extract_seq_model(pi: SquashedGaussianMLPActor) -> torch.nn.Sequential:
    if hasattr(pi, "get_seq"):
        net = pi.get_seq()
    else:
        modules = []

        for i, (name, m) in enumerate(pi.net.named_children()):
            modules.append(m)

        modules.append(pi.mu_layer)
        net = torch.nn.Sequential(*modules)
    return net


def extract_act_scale_bias(
    pi: SquashedGaussianMLPActor,
) -> Tuple[np.ndarray, np.ndarray]:
    act_scale: np.ndarray = pi.act_scale.detach().cpu().numpy()
    act_bias: np.ndarray = pi.act_bias.detach().cpu().numpy()

    return act_scale, act_bias


def are_seq_approx_eq(
    model1: torch.nn.Sequential,
    model2: torch.nn.Sequential,
) -> bool:
    return all(
        p1.data.equal(p2.data)
        for p1, p2 in zip(model1.parameters(), model2.parameters())
    )


def are_arr_approx_eq(
    arr1: np.ndarray,
    arr2: np.ndarray,
) -> bool:
    return np.array_equal(arr1, arr2)


def main():
    parser = argparse.ArgumentParser(
        description="Extract combined PyTorch actor model"
        "(continuous, deterministic, of net and mu_layer)"
    )
    parser.add_argument(
        "--model_path",
        "--mp",
        type=Path,
        required=True,
        help="Path to palaestrAI Actor model, saved with pytorch",
    )
    parser.add_argument(
        "--compare_model_path",
        "--cmp",
        type=Path,
        required=False,
        help="Path to compare palaestrAI Actor model to, saved with pytorch",
    )

    extraction_parser_group = parser.add_argument_group(
        "Extraction group",
        "Indicate, what should be extracted "
        "from the provided palaestrAI Actor",
    )

    extraction_parser_group.add_argument(
        "--extract_seq_model",
        "-es",
        action=argparse.BooleanOptionalAction,
        required=False,
        help="Extract the Sequential Linear/ReLU pytorch model ",
    )

    extraction_parser_group.add_argument(
        "--extract_act_scale_bias",
        "-ea",
        action=argparse.BooleanOptionalAction,
        required=False,
        help="Extract the act_scale and act_bias as numpy npz",
    )
    args = parser.parse_args()

    if not (args.extract_seq_model or args.extract_act_scale_bias):
        parser.error("No extraction requested, add -es and/or -ea")

    pi = get_pi(model_path=str(args.model_path))
    net = None
    act_scale, act_bias = None, None
    if args.extract_seq_model:
        dest_file_path = get_dest_file_path(args.model_path, "_pi_net_mu.pt")

        net = extract_seq_model(pi)
        torch.save(net, str(dest_file_path))

    if args.extract_act_scale_bias:
        dest_file_path = get_dest_file_path(
            args.model_path, "_pi_net_act_scale_bias.npz"
        )

        act_scale, act_bias = extract_act_scale_bias(pi)
        numpy.savez(dest_file_path, act_scale=act_scale, act_bias=act_bias)

    if args.compare_model_path:
        pi2 = get_pi(model_path=str(args.compare_model_path))
        net2 = extract_seq_model(pi2)
        print(f"Are nets equal? {are_seq_approx_eq(net, net2)}")
        print(args.model_path)
        print(f"Params: {[d.data for d in net.parameters()]}")
        print(args.compare_model_path)
        print(f"Params: {[d.data for d in net2.parameters()]}")

        if args.extract_act_scale_bias:
            assert (
                act_scale is not None and act_bias is not None,
                "Act_scale and act_bias need to be extracted to be "
                "compared",
            )
            act_scale2, act_bias2 = extract_act_scale_bias(pi2)

            act_scale_eq = are_arr_approx_eq(act_scale, act_scale2)
            print(f"Are act scales equal? {act_scale_eq}")

            act_bias_eq = are_arr_approx_eq(act_bias, act_bias2)
            print(f"Are act biases equal? {act_bias_eq}")


if __name__ == "__main__":
    main()
