
class Card:
    def __init__(self, name, intelligence, charisma, sport, humor, creativity, appearance):
        self.name = name
        self.intelligence = self._validate_stat(intelligence, "intelligence")
        self.charisma = self._validate_stat(charisma, "charisma")
        self.sport = self._validate_stat(sport, "sport")
        self.humor = self._validate_stat(humor, "humor")
        self.creativity = self._validate_stat(creativity, "creativity")
        self.appearance = self._validate_stat(appearance, "appearance")

    def _validate_stat(self, value, stat_name):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{stat_name.capitalize()} must be a number.")
        if value < 0:
            raise ValueError(f"{stat_name.capitalize()} must be non-negative.")
        return value

    def __repr__(self):
        return (f"Card({self.name}, {self.intelligence}, {self.charisma}, "
                f"{self.sport}, {self.humor}, {self.creativity}, {self.appearance})")

    def get_name(self):
        return self.name

    def get_intelligence(self):
        return self.intelligence

    def get_charisma(self):
        return self.charisma

    def get_sport(self):
        return self.sport

    def get_humor(self):
        return self.humor

    def get_creativity(self):
        return self.creativity

    def get_appearance(self):
        return self.appearance

    def set_name(self, name):
        self.name = name

    def set_intelligence(self, intelligence):
        self.intelligence = self._validate_stat(intelligence, "intelligence")

    def set_charisma(self, charisma):
        self.charisma = self._validate_stat(charisma, "charisma")

    def set_sport(self, sport):
        self.sport = self._validate_stat(sport, "sport")

    def set_humor(self, humor):
        self.humor = self._validate_stat(humor, "humor")

    def set_creativity(self, creativity):
        self.creativity = self._validate_stat(creativity, "creativity")

    def set_appearance(self, appearance):
        self.appearance = self._validate_stat(appearance, "appearance")
