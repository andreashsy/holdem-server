from enum import Enum

class Rank(Enum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = 't'
    JACK = 'j'
    QUEEN = 'q'
    KING = 'k'
    ACE = 'a'

    @classmethod
    def _member_list(cls):
        return list(cls)

    def __lt__(self, other):
        if not isinstance(other, Rank):
            raise NotImplementedError(f'Rank cannot be with {type(other)}')
        member_list = self.__class__._member_list()
        return member_list.index(self) < member_list.index(other)
    
    def __gt__(self, other):
        if not isinstance(other, Rank):
            raise NotImplementedError(f'Rank cannot be with {type(other)}')
        member_list = self.__class__._member_list()
        return member_list.index(self) > member_list.index(other)
