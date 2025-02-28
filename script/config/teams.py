from pydantic import BaseModel, field_validator


class Team(BaseModel):
    name: str
    needs_vulnbox: bool = True
    highlighted: bool = False


class TeamsConfig(BaseModel):
    teams: list[Team]

    @field_validator("teams")
    @classmethod
    def validate_teams(cls, teams):
        if len(teams) == 0:
            raise ValueError("Teams must contain at least one team")

        for team in teams:
            if list(map(lambda t: t.name == team.name, teams)).count(True) > 1:
                raise ValueError(f'Team "{team.name}" is registered multiple times')

        return teams
