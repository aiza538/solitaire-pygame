import sys
import os

original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
# Restore stdout
sys.stdout = original_stdout
import random
import copy

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CARD_WIDTH = 70
CARD_HEIGHT = 98
MAX_UNDO_STATES = 50

# Colors
GREEN = (53, 101, 77)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GOLD = (255, 215, 0)
DARK_GREEN = (35, 78, 56)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
EXIT_RED = (220, 60, 60)
EXIT_DARK_RED = (180, 40, 40)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Solitaire - All Cards Can Go to Empty Tableau")
clock = pygame.time.Clock()

# Node class for linked list
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

# Stack implementation
class Stack:
    def __init__(self):
        self.top = None
        self._size = 0
    
    def push(self, item):
        new_node = Node(item)
        new_node.next = self.top
        self.top = new_node
        self._size += 1
    
    def pop(self):
        if self.is_empty():
            return None
        popped_item = self.top.data
        self.top = self.top.next
        self._size -= 1
        return popped_item
    
    def peek(self):
        return self.top.data if self.top else None
    
    def is_empty(self):
        return self.top is None
    
    def size(self):
        return self._size
    
    def clear(self):
        self.top = None
        self._size = 0
    
    def __iter__(self):
        current = self.top
        while current:
            yield current.data
            current = current.next
    
    def to_list(self):
        result = []
        current = self.top
        while current:
            result.append(current.data)
            current = current.next
        return result

# Queue implementation
class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
        self._size = 0
    
    def enqueue(self, item):
        new_node = Node(item)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._size += 1
    
    def dequeue(self):
        if self.is_empty():
            return None
        dequeued_item = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return dequeued_item
    
    def peek(self):
        return self.front.data if self.front else None
    
    def is_empty(self):
        return self.front is None
    
    def size(self):
        return self._size
    
    def clear(self):
        self.front = self.rear = None
        self._size = 0
    
    def __iter__(self):
        current = self.front
        while current:
            yield current.data
            current = current.next
    
    def to_list(self):
        result = []
        current = self.front
        while current:
            result.append(current.data)
            current = current.next
        return result

# Single Linked List
class SingleLinkedList:
    def __init__(self):
        self.head = None
        self._size = 0
    
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1
    
    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1
    
    def remove_at_index(self, index):
        if index < 0 or index >= self._size:
            return None
        
        if index == 0:
            removed_data = self.head.data
            self.head = self.head.next
            self._size -= 1
            return removed_data
        
        current = self.head
        count = 0
        while current and count < index - 1:
            current = current.next
            count += 1
        
        if current and current.next:
            removed_data = current.next.data
            current.next = current.next.next
            self._size -= 1
            return removed_data
        return None
    
    def get_at_index(self, index):
        if index < 0 or index >= self._size:
            return None
        
        current = self.head
        count = 0
        while current and count < index:
            current = current.next
            count += 1
        return current.data if current else None
    
    def insert_at_index(self, index, data):
        if index < 0 or index > self._size:
            return False
        
        if index == 0:
            self.prepend(data)
            return True
        
        new_node = Node(data)
        current = self.head
        count = 0
        
        while current and count < index - 1:
            current = current.next
            count += 1
        
        if current:
            new_node.next = current.next
            current.next = new_node
            self._size += 1
            return True
        return False
    
    def size(self):
        return self._size
    
    def is_empty(self):
        return self.head is None
    
    def clear(self):
        self.head = None
        self._size = 0
    
    def get_last(self):
        if not self.head:
            return None
        current = self.head
        while current.next:
            current = current.next
        return current.data
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def from_list(self, items):
        self.clear()
        for item in items:
            self.append(item)

class Card:
    def __init__(self, suit, value, face_up=False):
        self.suit = suit
        self.value = value
        self.face_up = face_up
        self.image = None
        self.rect = None
        self.load_image()
    
    def load_image(self):
        self.create_beautiful_card()
    
    def create_beautiful_card(self):
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        
        if self.face_up:
            self.create_card_face()
        else:
            self.create_card_back()
    
    def create_card_face(self):
        self.image.fill(WHITE)
        pygame.draw.rect(self.image, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
        
        color = RED if self.suit in ['H', 'D'] else BLACK
        
        suit_symbol = ''
        if self.suit == 'H':
            suit_symbol = '♥'
        elif self.suit == 'D':
            suit_symbol = '♦'
        elif self.suit == 'C':
            suit_symbol = '♣'
        elif self.suit == 'S':
            suit_symbol = '♠'
        
        display_value = str(self.value)
        if self.value == 1:
            display_value = 'A'
        elif self.value == 11:
            display_value = 'J'
        elif self.value == 12:
            display_value = 'Q'
        elif self.value == 13:
            display_value = 'K'
        
        font_small = pygame.font.SysFont('arial', 16, bold=True)
        font_large = pygame.font.SysFont('arial', 24, bold=True)
        
        value_text = font_small.render(display_value, True, color)
        suit_text = font_small.render(suit_symbol, True, color)
        self.image.blit(value_text, (5, 5))
        self.image.blit(suit_text, (5, 22))
        
        center_suit = font_large.render(suit_symbol, True, color)
        suit_rect = center_suit.get_rect(center=(CARD_WIDTH//2, CARD_HEIGHT//2))
        self.image.blit(center_suit, suit_rect)
    
    def create_card_back(self):
        self.image.fill(BLUE)
        pygame.draw.rect(self.image, WHITE, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
        pygame.draw.rect(self.image, GOLD, (3, 3, CARD_WIDTH-6, CARD_HEIGHT-6), 1)
        
        for i in range(3):
            for j in range(4):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(self.image, GOLD, (10 + i*18, 10 + j*20, 12, 15))
    
    def draw(self, surface, x, y):
        self.rect.x = x
        self.rect.y = y
        surface.blit(self.image, (x, y))
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def __deepcopy__(self, memo):
        return Card(self.suit, self.value, self.face_up)
    
    def __str__(self):
        val = str(self.value)
        if self.value == 1: val = "A"
        elif self.value == 11: val = "J"
        elif self.value == 12: val = "Q"
        elif self.value == 13: val = "K"
        suit_char = {'H':'♥','D':'♦','C':'♣','S':'♠'}[self.suit]
        return f"{val}{suit_char}"

class Pile:
    def __init__(self, x, y, pile_type="tableau"):
        self.cards = SingleLinkedList()
        self.x = x
        self.y = y
        self.pile_type = pile_type
    
    def add_card(self, card):
        self.cards.append(card)
    
    def add_cards(self, cards_list):
        for card in cards_list:
            self.cards.append(card)
    
    def remove_card(self, index=-1):
        if self.cards.is_empty():
            return None
        if index == -1:
            return self.cards.remove_at_index(self.cards.size() - 1)
        return self.cards.remove_at_index(index)
    
    def remove_cards_from(self, start_index):
        if start_index >= self.cards.size():
            return []
        
        removed = []
        cards_to_remove = self.cards.size() - start_index
        for _ in range(cards_to_remove):
            card = self.cards.remove_at_index(start_index)
            if card:
                removed.append(card)
        return removed
    
    def get_top_card(self):
        if self.cards.is_empty():
            return None
        return self.cards.get_at_index(self.cards.size() - 1)
    
    def get_card_at_index(self, index):
        return self.cards.get_at_index(index)
    
    def size(self):
        return self.cards.size()
    
    def is_empty(self):
        return self.cards.is_empty()
    
    def get_all_cards(self):
        return self.cards.to_list()
    
    def set_cards(self, cards_list):
        self.cards.clear()
        for card in cards_list:
            self.cards.append(card)
    
    def draw(self, surface):
        if self.cards.is_empty():
            pygame.draw.rect(surface, WHITE, (self.x, self.y, CARD_WIDTH, CARD_HEIGHT), 2)
            pygame.draw.rect(surface, GOLD, (self.x+2, self.y+2, CARD_WIDTH-4, CARD_HEIGHT-4), 1)
            return
        
        if self.pile_type == "tableau":
            i = 0
            for card in self.cards:
                y_pos = self.y + i * 30
                card.draw(surface, self.x, y_pos)
                i += 1
        else:
            self.get_top_card().draw(surface, self.x, self.y)

class Game:
    def __init__(self):
        foundation_start_x = 80
        tableau_start_x = 80
        stock_x = SCREEN_WIDTH - 100
        waste_x = stock_x - CARD_WIDTH - 15
        
        self.tableau = SingleLinkedList()
        for i in range(7):
            pile = Pile(tableau_start_x + i * (CARD_WIDTH + 15), 200, "tableau")
            self.tableau.append(pile)
        
        self.foundations = SingleLinkedList()
        for i in range(4):
            pile = Pile(foundation_start_x + i * (CARD_WIDTH + 15), 60, "foundation")
            self.foundations.append(pile)
        
        self.stock_queue = Queue()
        self.waste_stack = Stack()
        
        self.stock_x = stock_x
        self.stock_y = 60
        self.waste_x = waste_x
        self.waste_y = 60
        
        # Drag state
        self.dragging = False
        self.drag_cards = []
        self.drag_source_pile = None
        self.drag_source_pile_type = None
        self.drag_start_index = -1
        self.drag_offset = (0, 0)
        self.last_click_time = 0
        
        self.moves = 0
        self.time = 0
        self.start_time = pygame.time.get_ticks()
        
        # Undo/Redo
        self.undo_stack = []
        self.redo_stack = []
        
        self.show_hint = False
        self.hint_from = None
        self.hint_to = None
        self.hint_card_rect = None
        self.game_won = False
        
        # Buttons
        self.exit_button_rect = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120, 100, 30)
        self.exit_button_hovered = False
        self.new_game_button_rect = pygame.Rect(SCREEN_WIDTH - 240, SCREEN_HEIGHT - 120, 100, 30)
        self.new_game_button_hovered = False
        self.undo_button_rect = pygame.Rect(SCREEN_WIDTH - 360, SCREEN_HEIGHT - 120, 100, 30)
        self.undo_button_hovered = False
        self.redo_button_rect = pygame.Rect(SCREEN_WIDTH - 480, SCREEN_HEIGHT - 120, 100, 30)
        self.redo_button_hovered = False
        
        self.create_deck()
        self.deal_cards()
        self.save_state()
    
    def save_state(self):
        tableau_state = []
        for i in range(7):
            pile = self.tableau.get_at_index(i)
            cards = [(card.suit, card.value, card.face_up) for card in pile.cards]
            tableau_state.append(cards)
        
        foundations_state = []
        for i in range(4):
            pile = self.foundations.get_at_index(i)
            cards = [(card.suit, card.value, card.face_up) for card in pile.cards]
            foundations_state.append(cards)
        
        stock_state = [(card.suit, card.value, card.face_up) for card in self.stock_queue]
        waste_state = [(card.suit, card.value, card.face_up) for card in self.waste_stack]
        
        self.undo_stack.append((tableau_state, foundations_state, stock_state, waste_state, self.moves))
        self.redo_stack.clear()
        
        while len(self.undo_stack) > MAX_UNDO_STATES:
            self.undo_stack.pop(0)
    
    def undo(self):
        if len(self.undo_stack) <= 1:
            return False
        
        tableau_state = []
        for i in range(7):
            pile = self.tableau.get_at_index(i)
            cards = [(card.suit, card.value, card.face_up) for card in pile.cards]
            tableau_state.append(cards)
        
        foundations_state = []
        for i in range(4):
            pile = self.foundations.get_at_index(i)
            cards = [(card.suit, card.value, card.face_up) for card in pile.cards]
            foundations_state.append(cards)
        
        stock_state = [(card.suit, card.value, card.face_up) for card in self.stock_queue]
        waste_state = [(card.suit, card.value, card.face_up) for card in self.waste_stack]
        
        self.redo_stack.append((tableau_state, foundations_state, stock_state, waste_state, self.moves))
        
        self.undo_stack.pop()
        self.load_state(self.undo_stack[-1])
        return True
    
    def redo(self):
        if not self.redo_stack:
            return False
        
        self.load_state(self.redo_stack.pop())
        return True
    
    def load_state(self, state):
        tableau_state, foundations_state, stock_state, waste_state, moves = state
        
        for i in range(7):
            pile = self.tableau.get_at_index(i)
            pile.cards.clear()
            for suit, value, face_up in tableau_state[i]:
                card = Card(suit, value, face_up)
                pile.cards.append(card)
        
        for i in range(4):
            pile = self.foundations.get_at_index(i)
            pile.cards.clear()
            for suit, value, face_up in foundations_state[i]:
                card = Card(suit, value, face_up)
                pile.cards.append(card)
        
        self.stock_queue.clear()
        for suit, value, face_up in stock_state:
            card = Card(suit, value, face_up)
            self.stock_queue.enqueue(card)
        
        self.waste_stack.clear()
        for suit, value, face_up in reversed(waste_state):
            card = Card(suit, value, face_up)
            self.waste_stack.push(card)
        
        self.moves = moves
    
    def create_deck(self):
        suits = ['H', 'D', 'C', 'S']
        self.deck = SingleLinkedList()
        for suit in suits:
            for value in range(1, 14):
                self.deck.append(Card(suit, value))
        self.shuffle_deck()
    
    def shuffle_deck(self):
        cards = self.deck.to_list()
        random.shuffle(cards)
        self.deck.clear()
        for card in cards:
            self.deck.append(card)
    
    def deal_cards(self):
        for i in range(7):
            self.tableau.get_at_index(i).cards.clear()
        
        self.stock_queue.clear()
        self.waste_stack.clear()
        
        cards = self.deck.to_list()
        card_idx = 0
        
        for i in range(7):
            for j in range(i, 7):
                if card_idx < len(cards):
                    card = cards[card_idx]
                    card.face_up = (j == i)
                    card.load_image()
                    self.tableau.get_at_index(j).add_card(card)
                    card_idx += 1
        
        while card_idx < len(cards):
            card = cards[card_idx]
            card.face_up = False
            card.load_image()
            self.stock_queue.enqueue(card)
            card_idx += 1
    
    def restart_game(self):
        self.create_deck()
        self.deal_cards()
        self.moves = 0
        self.start_time = pygame.time.get_ticks()
        self.game_won = False
        self.show_hint = False
        self.dragging = False
        self.drag_cards = []
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.save_state()
    
    def check_win_condition(self):
        for i in range(4):
            if self.foundations.get_at_index(i).size() != 13:
                return False
        return True
    
    def get_valid_drag_sequence(self, pile, start_index):
        if start_index >= pile.size():
            return []
        
        first_card = pile.get_card_at_index(start_index)
        if not first_card.face_up:
            return []
        
        valid_sequence = [first_card]
        
        for i in range(start_index + 1, pile.size()):
            prev_card = pile.get_card_at_index(i - 1)
            curr_card = pile.get_card_at_index(i)
            
            if not curr_card.face_up:
                break
            
            prev_is_red = (prev_card.suit in ['H', 'D'])
            curr_is_red = (curr_card.suit in ['H', 'D'])
            
            if prev_is_red != curr_is_red and prev_card.value == curr_card.value + 1:
                valid_sequence.append(curr_card)
            else:
                break
        
        return valid_sequence
    
    def can_drop_on_foundation(self, pile, card):
        if pile.is_empty():
            return card.value == 1
        top_card = pile.get_top_card()
        return (card.suit == top_card.suit and card.value == top_card.value + 1)
    
    # ========== FIXED: ALL CARDS CAN GO TO EMPTY TABLEAU ==========
    def can_drop_on_tableau(self, pile, card):
        """
        UPDATED RULE: 
        - EMPTY TABLEAU: ANY card can be placed (King, Queen, Jack, 10, 9, 8, 7, 6, 5, 4, 3, 2, Ace)
        - NON-EMPTY TABLEAU: Colors must alternate, value must be 1 less than top card
        """
        # EMPTY TABLEAU: AB KOI BHI CARD JA SAKTA HAI!
        if pile.is_empty():
            return True  # <-- FIXED: Sab cards allowed
        
        top_card = pile.get_top_card()
        if not top_card:
            return True
        
        card_is_red = (card.suit in ['H', 'D'])
        top_is_red = (top_card.suit in ['H', 'D'])
        
        return (card_is_red != top_is_red) and (card.value == top_card.value - 1)
    # ===============================================================
    
    def can_drop_sequence_on_tableau(self, pile, cards):
        if not cards:
            return False
        return self.can_drop_on_tableau(pile, cards[0])
    
    def find_hint(self):
        if not self.waste_stack.is_empty():
            waste_card = self.waste_stack.peek()
            for i in range(4):
                if self.can_drop_on_foundation(self.foundations.get_at_index(i), waste_card):
                    return ("Waste", f"Foundation {i+1}", waste_card, self.waste_x, self.waste_y)
        
        for i in range(7):
            pile = self.tableau.get_at_index(i)
            if not pile.is_empty():
                top_card = pile.get_top_card()
                if top_card.face_up:
                    for j in range(4):
                        if self.can_drop_on_foundation(self.foundations.get_at_index(j), top_card):
                            y_pos = pile.y + (pile.size() - 1) * 30
                            return (f"Tableau {i+1}", f"Foundation {j+1}", top_card, pile.x, y_pos)
        
        for i in range(7):
            from_pile = self.tableau.get_at_index(i)
            for card_idx in range(from_pile.size()):
                card = from_pile.get_card_at_index(card_idx)
                if card.face_up:
                    sequence = self.get_valid_drag_sequence(from_pile, card_idx)
                    if sequence:
                        for j in range(7):
                            if i != j:
                                to_pile = self.tableau.get_at_index(j)
                                if self.can_drop_sequence_on_tableau(to_pile, sequence):
                                    y_pos = from_pile.y + card_idx * 30
                                    return (f"Tableau {i+1}", f"Tableau {j+1}", card, from_pile.x, y_pos)
        
        if not self.stock_queue.is_empty():
            return ("Stock", "Waste", None, self.stock_x, self.stock_y)
        
        return None
    
    def handle_stock_click(self):
        if not self.stock_queue.is_empty():
            card = self.stock_queue.dequeue()
            card.face_up = True
            card.load_image()
            self.waste_stack.push(card)
            self.moves += 1
            self.save_state()
        elif not self.waste_stack.is_empty():
            waste_cards = []
            while not self.waste_stack.is_empty():
                waste_cards.append(self.waste_stack.pop())
            for card in reversed(waste_cards):
                card.face_up = False
                card.load_image()
                self.stock_queue.enqueue(card)
            self.moves += 1
            self.save_state()
        
        self.show_hint = False
    
    def start_drag(self, source_pile, source_type, cards, start_index, offset_x, offset_y):
        self.dragging = True
        self.drag_source_pile = source_pile
        self.drag_source_pile_type = source_type
        self.drag_start_index = start_index
        self.drag_cards = cards
        self.drag_offset = (offset_x, offset_y)
    
    def start_drag_tableau(self, pile, card_index):
        cards_to_drag = self.get_valid_drag_sequence(pile, card_index)
        if not cards_to_drag:
            return
        
        for _ in range(len(cards_to_drag)):
            pile.remove_card(card_index)
        
        self.start_drag(
            pile, "tableau", cards_to_drag, card_index,
            pygame.mouse.get_pos()[0] - pile.x,
            pygame.mouse.get_pos()[1] - (pile.y + card_index * 30)
        )
    
    def start_drag_waste(self):
        card = self.waste_stack.pop()
        if not card:
            return
        
        self.start_drag(
            None, "waste", [card], -1,
            pygame.mouse.get_pos()[0] - self.waste_x,
            pygame.mouse.get_pos()[1] - self.waste_y
        )
    
    def start_drag_foundation(self, pile):
        card = pile.remove_card()
        if not card:
            return
        
        self.start_drag(
            pile, "foundation", [card], -1,
            pygame.mouse.get_pos()[0] - pile.x,
            pygame.mouse.get_pos()[1] - pile.y
        )
    
    def complete_drag(self, dest_pile, dest_type):
        if not self.drag_cards:
            return False
        
        if dest_type == "foundation":
            if len(self.drag_cards) != 1:
                return False
            if not self.can_drop_on_foundation(dest_pile, self.drag_cards[0]):
                return False
        else:
            if not self.can_drop_sequence_on_tableau(dest_pile, self.drag_cards):
                return False
        
        for card in self.drag_cards:
            dest_pile.add_card(card)
        
        if self.drag_source_pile_type == "tableau" and self.drag_source_pile:
            if not self.drag_source_pile.is_empty():
                top = self.drag_source_pile.get_top_card()
                if top and not top.face_up:
                    top.face_up = True
                    top.load_image()
        
        self.moves += 1
        self.save_state()
        return True
    
    def cancel_drag(self):
        if self.drag_source_pile_type == "tableau" and self.drag_source_pile:
            for i, card in enumerate(self.drag_cards):
                self.drag_source_pile.cards.insert_at_index(self.drag_start_index + i, card)
        elif self.drag_source_pile_type == "waste":
            for card in reversed(self.drag_cards):
                self.waste_stack.push(card)
        elif self.drag_source_pile_type == "foundation" and self.drag_source_pile:
            for card in self.drag_cards:
                self.drag_source_pile.add_card(card)
        
        self.dragging = False
        self.drag_cards = []
        self.drag_source_pile = None
    
    def handle_click(self, pos):
        if self.game_won:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click_time < 150:
            return
        self.last_click_time = current_time
        
        if self.undo_button_rect.collidepoint(pos):
            self.undo()
            return
        if self.redo_button_rect.collidepoint(pos):
            self.redo()
            return
        if self.new_game_button_rect.collidepoint(pos):
            self.restart_game()
            return
        if self.exit_button_rect.collidepoint(pos):
            pygame.quit()
            sys.exit()
        
        hint_button = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 65, 100, 30)
        if hint_button.collidepoint(pos):
            self.show_hint = not self.show_hint
            if self.show_hint:
                hint = self.find_hint()
                if hint:
                    self.hint_from, self.hint_to, card, x, y = hint
                    self.hint_card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
                else:
                    self.hint_card_rect = None
            return
        
        stock_rect = pygame.Rect(self.stock_x, self.stock_y, CARD_WIDTH, CARD_HEIGHT)
        if stock_rect.collidepoint(pos):
            self.handle_stock_click()
            return
        
        if not self.waste_stack.is_empty():
            waste_card = self.waste_stack.peek()
            if waste_card.is_clicked(pos):
                self.start_drag_waste()
                return
        
        for i in range(4):
            pile = self.foundations.get_at_index(i)
            if not pile.is_empty():
                if pile.get_top_card().is_clicked(pos):
                    self.start_drag_foundation(pile)
                    return
        
        for i in range(7):
            pile = self.tableau.get_at_index(i)
            for idx in range(pile.size() - 1, -1, -1):
                card = pile.get_card_at_index(idx)
                if card.face_up and card.is_clicked(pos):
                    self.start_drag_tableau(pile, idx)
                    return
    
    def handle_release(self, pos):
        if not self.dragging or not self.drag_cards:
            self.dragging = False
            self.drag_cards = []
            return
        
        dropped = False
        
        for i in range(4):
            foundation = self.foundations.get_at_index(i)
            rect = pygame.Rect(foundation.x, foundation.y, CARD_WIDTH, CARD_HEIGHT)
            if rect.collidepoint(pos):
                if self.complete_drag(foundation, "foundation"):
                    dropped = True
                break
        
        if not dropped:
            for i in range(7):
                tableau = self.tableau.get_at_index(i)
                if tableau.is_empty():
                    rect = pygame.Rect(tableau.x, tableau.y, CARD_WIDTH, CARD_HEIGHT)
                else:
                    rect = pygame.Rect(tableau.x, tableau.y, CARD_WIDTH, CARD_HEIGHT + (tableau.size() - 1) * 30)
                
                if rect.collidepoint(pos):
                    if self.complete_drag(tableau, "tableau"):
                        dropped = True
                    break
        
        if not dropped:
            self.cancel_drag()
        
        self.dragging = False
        self.drag_cards = []
        self.drag_source_pile = None
        self.show_hint = False
    
    def draw(self, surface):
        surface.fill(DARK_GREEN)
        
        for pile in self.foundations:
            pile.draw(surface)
        
        for pile in self.tableau:
            pile.draw(surface)
        
        stock_rect = pygame.Rect(self.stock_x, self.stock_y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surface, WHITE, stock_rect, 2)
        pygame.draw.rect(surface, GOLD, (self.stock_x+2, self.stock_y+2, CARD_WIDTH-4, CARD_HEIGHT-4), 1)
        if not self.stock_queue.is_empty():
            back = pygame.Surface((CARD_WIDTH-4, CARD_HEIGHT-4), pygame.SRCALPHA)
            back.fill(BLUE)
            pygame.draw.rect(back, WHITE, (0, 0, CARD_WIDTH-4, CARD_HEIGHT-4), 2)
            pygame.draw.rect(back, GOLD, (2, 2, CARD_WIDTH-8, CARD_HEIGHT-8), 1)
            surface.blit(back, (self.stock_x+2, self.stock_y+2))
        
        waste_rect = pygame.Rect(self.waste_x, self.waste_y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surface, WHITE, waste_rect, 2)
        pygame.draw.rect(surface, GOLD, (self.waste_x+2, self.waste_y+2, CARD_WIDTH-4, CARD_HEIGHT-4), 1)
        if not self.waste_stack.is_empty():
            self.waste_stack.peek().draw(surface, self.waste_x, self.waste_y)
        
        if self.show_hint and self.hint_card_rect:
            pygame.draw.rect(surface, YELLOW, self.hint_card_rect, 3)
        
        if self.dragging and self.drag_cards:
            mx, my = pygame.mouse.get_pos()
            for i, card in enumerate(self.drag_cards):
                card.draw(surface, mx - self.drag_offset[0], my - self.drag_offset[1] + i * 25)
        
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, (40, 40, 40), panel_rect)
        pygame.draw.line(surface, GOLD, (0, SCREEN_HEIGHT - 80), (SCREEN_WIDTH, SCREEN_HEIGHT - 80), 2)
        
        font = pygame.font.SysFont('arial', 20, bold=True)
        small_font = pygame.font.SysFont('arial', 16)
        
        moves_text = font.render(f"Moves: {self.moves}", True, WHITE)
        time_text = font.render(f"Time: {self.time//60:02d}:{self.time%60:02d}", True, WHITE)
        surface.blit(moves_text, (20, SCREEN_HEIGHT - 70))
        surface.blit(time_text, (180, SCREEN_HEIGHT - 70))
        
        hint_btn = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 65, 100, 30)
        pygame.draw.rect(surface, LIGHT_BLUE, hint_btn)
        hint_text = small_font.render("Hint (H)", True, BLACK)
        surface.blit(hint_text, (SCREEN_WIDTH - 110, SCREEN_HEIGHT - 60))
        
        label_font = pygame.font.SysFont('arial', 18, bold=True)
        surface.blit(label_font.render("FOUNDATION", True, GOLD), (80, 35))
        surface.blit(label_font.render("TABLEAU", True, GOLD), (80, 175))
        surface.blit(label_font.render("STOCK", True, WHITE), (self.stock_x, 35))
        surface.blit(label_font.render("WASTE", True, WHITE), (self.waste_x, 35))
        
        undo_color = DARK_GREEN if self.undo_button_hovered else GREEN
        pygame.draw.rect(surface, undo_color, self.undo_button_rect)
        pygame.draw.rect(surface, WHITE, self.undo_button_rect, 2)
        surface.blit(small_font.render("Undo (Z)", True, WHITE), 
                    (self.undo_button_rect.x + 20, self.undo_button_rect.y + 7))
        
        redo_color = DARK_GREEN if self.redo_button_hovered else GREEN
        pygame.draw.rect(surface, redo_color, self.redo_button_rect)
        pygame.draw.rect(surface, WHITE, self.redo_button_rect, 2)
        surface.blit(small_font.render("Redo (Y)", True, WHITE), 
                    (self.redo_button_rect.x + 20, self.redo_button_rect.y + 7))
        
        new_color = DARK_GREEN if self.new_game_button_hovered else GREEN
        pygame.draw.rect(surface, new_color, self.new_game_button_rect)
        pygame.draw.rect(surface, WHITE, self.new_game_button_rect, 2)
        surface.blit(small_font.render("New Game", True, WHITE), 
                    (self.new_game_button_rect.x + 20, self.new_game_button_rect.y + 7))
        
        exit_color = EXIT_DARK_RED if self.exit_button_hovered else EXIT_RED
        pygame.draw.rect(surface, exit_color, self.exit_button_rect)
        pygame.draw.rect(surface, WHITE, self.exit_button_rect, 2)
        surface.blit(small_font.render("Exit", True, WHITE), 
                    (self.exit_button_rect.x + 30, self.exit_button_rect.y + 7))
        
        if self.show_hint and self.hint_from:
            status = small_font.render(f"Hint: Move from {self.hint_from} to {self.hint_to}", True, LIGHT_BLUE)
            surface.blit(status, (350, SCREEN_HEIGHT - 70))
        elif not self.show_hint:
            status = small_font.render("Click stock to draw. Drag cards to move. H for hint | ALL cards can go to empty tableau", True, GOLD)
            surface.blit(status, (350, SCREEN_HEIGHT - 70))
        
        if self.game_won:
            win_font = pygame.font.SysFont('arial', 48, bold=True)
            win_text = win_font.render("🎉 YOU WIN! 🎉", True, GOLD)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            bg_rect = pygame.Rect(win_rect.x - 20, win_rect.y - 20, win_rect.width + 40, win_rect.height + 40)
            pygame.draw.rect(surface, DARK_GREEN, bg_rect)
            pygame.draw.rect(surface, GOLD, bg_rect, 4)
            surface.blit(win_text, win_rect)
            
            stats_text = small_font.render(f"Moves: {self.moves} | Time: {self.time//60:02d}:{self.time%60:02d}", True, WHITE)
            stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            surface.blit(stats_text, stats_rect)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        self.time = (current_time - self.start_time) // 1000
        
        if not self.game_won and self.check_win_condition():
            self.game_won = True
        
        mouse_pos = pygame.mouse.get_pos()
        self.exit_button_hovered = self.exit_button_rect.collidepoint(mouse_pos)
        self.new_game_button_hovered = self.new_game_button_rect.collidepoint(mouse_pos)
        self.undo_button_hovered = self.undo_button_rect.collidepoint(mouse_pos)
        self.redo_button_hovered = self.redo_button_rect.collidepoint(mouse_pos)

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.handle_release(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    game.show_hint = not game.show_hint
                    if game.show_hint:
                        hint = game.find_hint()
                        if hint:
                            game.hint_from, game.hint_to, card, x, y = hint
                            game.hint_card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
                elif event.key == pygame.K_n:
                    game.restart_game()
                elif event.key == pygame.K_z:
                    game.undo()
                elif event.key == pygame.K_y:
                    game.redo()
        
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()