import logging as log
from SpiffyWorld import UnitDialogue

class UnitDialogueCollection:
    """
    Representation of persisted dialogues on a unit
    """
    def __init__(self, **kwargs):
        self.dialogue = []

    def add(self, dialogue):
        if not isinstance(dialogue, UnitDialogue):
            raise ValueError("dialogue must be an instance of UnitDialogue")

        if dialogue not in self.dialogue:
            self.dialogue.append(dialogue)

    def get_dialogue_by_context(self, **kwargs):
        context = kwargs["context"]
        dialogue = None
        generic_user_id = 0
        generic_dialogue = self.dialogue[generic_user_id]
        dialogues = [d for d in generic_dialogue if d["context"] == context]

        if len(dialogues) > 0:
            random_dialogue = random.choice(dialogues)
            dialogue = random_dialogue["dialogue"]

        return dialogue

    def get_dialogue_by_dialogue_id_list(self, dialogue_id_list):
        return [dialogue for dialogue in self.dialogue if dialogue.id in dialogue_id_list]
