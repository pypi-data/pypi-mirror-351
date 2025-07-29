from dataclasses import dataclass


@dataclass
class DeadlineRow:
    dataset_id: str
    deadline_minute: str
    deadline_hour: str
    deadline_day_of_the_month: str
    deadline_month: str
    deadline_day_of_week: str
    deadline_year: str
    timezone: str
    file_frequency: str
    is_active: str
    is_excluded: str

    def to_key(self):
        return (
            self.dataset_id,
            self.deadline_minute,
            self.deadline_hour,
            self.deadline_day_of_the_month,
            self.deadline_month,
            self.deadline_day_of_week,
            self.deadline_year,
            self.timezone,
            self.file_frequency,
            self.is_active,
            self.is_excluded,
        )
