import datetime
from back.fit.utils import get_intensity, get_path

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.workout_message import WorkoutMessage
from fit_tool.profile.messages.workout_step_message import WorkoutStepMessage
from fit_tool.profile.profile_type import (FileType, Intensity, Manufacturer,
                                           Sport, WorkoutStepDuration,
                                           WorkoutStepTarget, Intensity)


# SPEED mm/s EX: 4'16/k = 3'91m/s = 3_910mm/s
# TIME ms EX: 20min = 1_200_000


class WorkoutWriter:
    def __init__(self, sport: str, workout: dict, id: str, user: int):
        self.sport = sport
        self.workout = workout
        self.builder = FitFileBuilder(auto_define=True, min_string_size=50)
        self.id = id
        self.user = user
        self._path = None

    @property
    def path(self):
        if self._path is None:
            path = get_path(self.user)
            self._path = path + f'/{self.id}.fit'
            return self._path
        return self._path

    def _write_id_message(self):
        file_id_message = FileIdMessage()
        file_id_message.type = FileType.WORKOUT
        file_id_message.manufacturer = Manufacturer.DEVELOPMENT.value
        file_id_message.product = 0
        file_id_message.time_created = round(
            datetime.datetime.now().timestamp() * 1000)
        file_id_message.serial_number = 0x12345678
        return file_id_message

    def _write_wkt_message(self, name, workout_steps):
        workout_message = WorkoutMessage()
        workout_message.workout_name = name
        if self.sport == 'running':
            workout_message.sport = Sport.RUNNING
        elif self.sport == 'cycling':
            workout_message.sport = Sport.CYCLING
        workout_message.num_valid_steps = workout_steps
        return workout_message

    def _write_step(self, name, duration, target_value):
        step = WorkoutStepMessage()
        step.duration_type = WorkoutStepDuration.TIME
        # Convert minute to ms
        step.duration_value = duration * 60 * 1000
        if self.sport == 'running':
            step.target_type = WorkoutStepTarget.SPEED
            # Convert km/h to mm/s
            target_value = round((target_value * 1000) / 3600, 4) * 1000
            low_target_value = target_value - (target_value*0.01)
            high_target_value = target_value + (target_value*0.01)
            step.target_value = 0
            step.custom_target_speed_low = low_target_value
            step.custom_target_speed_high = high_target_value

        elif self.sport == 'cycling':
            step.target_type = WorkoutStepTarget.POWER
            step.target_value = target_value
        else:
            pass
        step.workout_step_name = name
        step.intensity = get_intensity(name.lower())
        return step

    def write_workout(self):
        workout = WorkoutMessage()
        workout.sport = Sport.RUNNING

        steps = []
        # write warmup step
        steps.append(self._write_step("Warmup", self.workout["warmup"]["timer"], self.workout["warmup"]["work"]))

        # for now just write one step and will break if not step_
        for set_key, set_steps in self.workout["set_1"].items():
            steps.append(self._write_step("active", set_steps["active"]["timer"], set_steps["active"]["work"]))
            steps.append(self._write_step("rest", set_steps["rest"]["timer"], set_steps["rest"]["work"]))

        # write cooldown step
        steps.append(self._write_step("Cooldown", self.workout["cooldown"]["timer"], self.workout["cooldown"]["timer"]))

        self.builder.add(self._write_id_message())
        self.builder.add(self._write_wkt_message("5*4min", len(steps)))
        self.builder.add_all(steps)

        fit_file = self.builder.build()
        fit_file.to_file(self.path)


if __name__ == "__main__":
    workout_dict = {
        "warmup": {"timer": 10, "work": 10.5},
        "set_1": {
            "step_0": {"active": {"timer": 4, "work": 15.0}, "rest": {"timer": 2, "work": 10.0}},
            "step_1": {"active": {"timer": 4, "work": 15.0}, "rest": {"timer": 2, "work": 10.0}},
            "step_2": {"active": {"timer": 4, "work": 15.0}, "rest": {"timer": 2, "work": 10.0}},
            "step_3": {"active": {"timer": 4, "work": 15.0}, "rest": {"timer": 2, "work": 10.0}},
            "step_4": {"active": {"timer": 4, "work": 15.0}, "rest": {"timer": 2, "work": 10.0}}
        },
        "cooldown": {"timer": 10, "work": 10.5}
    }
    builder = WorkoutWriter("running", workout_dict, "123", 1)
    builder.write_workout()
