from .midi_analysis.MidiEvents import ControllerEvent


class CCData:

    def __init__(self, midi_track, frames_per_second, frame_offset: int):
        # map controller number to CCControllerData
        self.cc_controller_data = {}
        self.frames_per_second = frames_per_second
        self.frame_offset = frame_offset
        for event in midi_track.events:
            if isinstance(event, ControllerEvent):
                self.cc_controller_data.setdefault(event.controller_type,
                                                   CCControllerData(frames_per_second, frame_offset)) \
                    .add_event_data(event)

    def get_cc_controller_data(self, controller_number: int):
        return self.cc_controller_data[controller_number]


class CCControllerData:
    def __init__(self, frames_per_second, frame_offset: int):
        self.frames_per_second = frames_per_second
        self.frame_offset = frame_offset
        self.cc_event_data = []
        self.values_map = {}  # map frame to value
        # used to keep track of current frame when adding to value dictionary
        self.__current_value = 0
        # used to keep track of current value when adding to value dictionary
        self.__current_frame = 0

    def add_event_data(self, controller_event):
        cc_event_data = CCEventData(controller_event, self.frames_per_second, self.frame_offset)
        self.cc_event_data.append(cc_event_data)
        while self.__current_frame < cc_event_data.time_frames:
            self.values_map[self.__current_frame] = self.__current_value
            self.__current_frame += 1
        self.__current_frame = cc_event_data.time_frames
        self.__current_value = cc_event_data.value
        self.values_map[self.__current_frame] = self.__current_value

    def min_max(self):
        if self.cc_event_data:
            values = [x.value for x in self.cc_event_data]
            return min(values), max(values)
        else:
            return None

    def value_at_frame(self, frame: int):
        return self.values_map.get(frame, self.__current_value)


class CCEventData:
    def __init__(self, controller_event, frames_per_second: float, frame_offset: int):
        self.time_ms = controller_event.start_time
        self.value = controller_event.value
        self.time_frames = int((self.time_ms / 1000) * frames_per_second + frame_offset)
