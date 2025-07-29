from vut.mapping import (
    load_action_mapping,
    load_class_mapping,
    load_video_action_mapping,
    load_video_boundaries,
)
from vut.util import Env


class Base:
    env = Env()
    text_to_index: dict[str, int]
    index_to_text: dict[int, str]
    action_to_steps: dict[str, list[str]]
    video_to_action: dict[str, str]
    video_boundaries: dict[str, list[tuple[int, int]]]
    backgrounds: list[str]

    def __init__(
        self,
        class_mapping_path: str = None,
        class_mapping_has_header: bool = False,
        class_mapping_separator: str = ",",
        action_mapping_path: str = None,
        action_mapping_has_header: bool = False,
        action_mapping_action_separator: str = ",",
        action_mapping_step_separator: str = " ",
        video_action_mapping_path: str = None,
        video_action_mapping_has_header: bool = False,
        video_action_mapping_separator: str = ",",
        video_boundary_dir_path: str = None,
        video_boundary_has_header: bool = False,
        video_boundary_separator: str = ",",
        backgrounds: list[str] = None,
    ):
        """Initialize the Base class.

        Args:
            class_mapping_path (str, optional): Path to the class mapping file. Defaults to None.
            class_mapping_has_header (bool, optional): Whether the class mapping file has a header. Defaults to False.
            class_mapping_separator (str, optional): Separator used in the class mapping file. Defaults to ",".
            action_mapping_path (str, optional): Path to the action mapping file. Defaults to None.
            action_mapping_has_header (bool, optional): Whether the action mapping file has a header. Defaults to False.
            action_mapping_action_separator (str, optional): Separator used for actions in the action mapping file. Defaults to ",".
            action_mapping_step_separator (str, optional): Separator used for steps in the action mapping file. Defaults to " ".
            video_action_mapping_path (str, optional): Path to the video action mapping file. Defaults to None.
            video_action_mapping_has_header (bool, optional): Whether the video action mapping file has a header. Defaults to False.
            video_action_mapping_separator (str, optional): Separator used in the video action mapping file. Defaults to ",".
            video_boundary_dir_path (str, optional): Path to the video boundary directory. Defaults to None.
            video_boundary_has_header (bool, optional): Whether the video boundary files have headers. Defaults to False.
            video_boundary_separator (str, optional): Separator used in the video boundary files. Defaults to ",".
            backgrounds (list[str], optional): List of background images. Defaults to None.
        """
        if class_mapping_path is not None:
            text_to_index, index_to_text = load_class_mapping(
                class_mapping_path,
                has_header=class_mapping_has_header,
                separator=class_mapping_separator,
            )
            self.text_to_index = text_to_index
            self.index_to_text = index_to_text
        else:
            self.text_to_index = {}
            self.index_to_text = {}
        if action_mapping_path is not None:
            action_to_steps = load_action_mapping(
                action_mapping_path,
                has_header=action_mapping_has_header,
                action_separator=action_mapping_action_separator,
                step_separator=action_mapping_step_separator,
            )
            self.action_to_steps = action_to_steps
        else:
            self.action_to_steps = {}
        if video_action_mapping_path is not None:
            video_to_action = load_video_action_mapping(
                video_action_mapping_path,
                has_header=video_action_mapping_has_header,
                separator=video_action_mapping_separator,
            )
            self.video_to_action = video_to_action
        else:
            self.video_to_action = {}
        if video_boundary_dir_path is not None:
            video_boundaries = load_video_boundaries(
                video_boundary_dir_path,
                has_header=video_boundary_has_header,
                separator=video_boundary_separator,
            )
            self.video_boundaries = video_boundaries
        else:
            self.video_boundaries = {}
        if backgrounds is not None:
            self.backgrounds = backgrounds
        else:
            self.backgrounds = []
