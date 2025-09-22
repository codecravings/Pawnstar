"""
Tactical pattern recognition for chess positions
"""

import chess
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass
class TacticalPattern:
    name: str
    description: str
    attacking_square: str
    target_squares: List[str]
    pattern_type: str
    severity: str  # "minor", "major", "critical"
    emoji: str

class TacticalAnalyzer:
    def __init__(self):
        self.pattern_types = {
            "fork": {"emoji": "🍴", "description": "Attacks multiple pieces"},
            "pin": {"emoji": "📌", "description": "Piece cannot move due to valuable piece behind"},
            "skewer": {"emoji": "🗡️", "description": "Forces valuable piece to move, exposing less valuable piece"},
            "discovered_attack": {"emoji": "🔍", "description": "Moving one piece reveals attack from another"},
            "double_attack": {"emoji": "⚔️", "description": "Two pieces attacking same target"},
            "deflection": {"emoji": "🔄", "description": "Forces defending piece away"},
            "decoy": {"emoji": "🎯", "description": "Lures piece to unfavorable square"},
            "removal": {"emoji": "🚫", "description": "Removes defending piece"},
            "zugzwang": {"emoji": "🔒", "description": "Any move worsens position"},
            "trapped_piece": {"emoji": "🕳️", "description": "Piece has no safe moves"}
        }
    
    def analyze_position(self, board: chess.Board) -> List[TacticalPattern]:
        """Analyze a chess position for tactical patterns"""
        patterns = []
        
        # Analyze for each color
        for color in [chess.WHITE, chess.BLACK]:
            patterns.extend(self._find_forks(board, color))
            patterns.extend(self._find_pins(board, color))
            patterns.extend(self._find_skewers(board, color))
            patterns.extend(self._find_discovered_attacks(board, color))
            patterns.extend(self._find_trapped_pieces(board, color))
            patterns.extend(self._find_double_attacks(board, color))
        
        return patterns
    
    def _find_forks(self, board: chess.Board, color: chess.Color) -> List[TacticalPattern]:
        """Find fork patterns - one piece attacking multiple targets"""
        patterns = []
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece or piece.color != color:
                continue
                
            # Get all squares this piece attacks
            attacked_squares = []
            for target_square in chess.SQUARES:
                if board.is_attacked_by(color, target_square):
                    target_piece = board.piece_at(target_square)
                    if target_piece and target_piece.color != color:
                        # Check if this specific piece can attack the target
                        if self._piece_attacks_square(board, square, target_square):
                            attacked_squares.append(target_square)
            
            # A fork requires attacking at least 2 valuable pieces
            if len(attacked_squares) >= 2:
                # Check if targets are valuable (not just pawns)
                valuable_targets = []
                for target_sq in attacked_squares:
                    target_piece = board.piece_at(target_sq)
                    if target_piece and target_piece.piece_type != chess.PAWN:
                        valuable_targets.append(target_sq)
                
                if len(valuable_targets) >= 2:
                    severity = self._calculate_fork_severity(board, valuable_targets)
                    patterns.append(TacticalPattern(
                        name="Fork",
                        description=f"{piece.symbol().upper()} forks {len(valuable_targets)} pieces",
                        attacking_square=chess.square_name(square),
                        target_squares=[chess.square_name(sq) for sq in valuable_targets],
                        pattern_type="fork",
                        severity=severity,
                        emoji="🍴"
                    ))
        
        return patterns
    
    def _find_pins(self, board: chess.Board, color: chess.Color) -> List[TacticalPattern]:
        """Find pin patterns - piece cannot move due to valuable piece behind"""
        patterns = []
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece or piece.color != color:
                continue
            
            # Only sliding pieces (rook, bishop, queen) can create pins
            if piece.piece_type not in [chess.ROOK, chess.BISHOP, chess.QUEEN]:
                continue
            
            # Check each direction this piece can move
            for direction in self._get_piece_directions(piece.piece_type):
                pinned_piece, valuable_piece = self._find_pin_in_direction(board, square, direction, color)
                if pinned_piece and valuable_piece:
                    severity = self._calculate_pin_severity(board, valuable_piece)
                    patterns.append(TacticalPattern(
                        name="Pin",
                        description=f"Pinned piece cannot move safely",
                        attacking_square=chess.square_name(square),
                        target_squares=[chess.square_name(pinned_piece), chess.square_name(valuable_piece)],
                        pattern_type="pin",
                        severity=severity,
                        emoji="📌"
                    ))
        
        return patterns
    
    def _find_skewers(self, board: chess.Board, color: chess.Color) -> List[TacticalPattern]:
        """Find skewer patterns - valuable piece forced to move, exposing less valuable piece"""
        patterns = []
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece or piece.color != color:
                continue
            
            # Only sliding pieces can create skewers
            if piece.piece_type not in [chess.ROOK, chess.BISHOP, chess.QUEEN]:
                continue
            
            for direction in self._get_piece_directions(piece.piece_type):
                front_piece, back_piece = self._find_skewer_in_direction(board, square, direction, color)
                if front_piece and back_piece:
                    severity = self._calculate_skewer_severity(board, front_piece, back_piece)
                    patterns.append(TacticalPattern(
                        name="Skewer",
                        description=f"Valuable piece must move, exposing piece behind",
                        attacking_square=chess.square_name(square),
                        target_squares=[chess.square_name(front_piece), chess.square_name(back_piece)],
                        pattern_type="skewer",
                        severity=severity,
                        emoji="🗡️"
                    ))
        
        return patterns
    
    def _find_discovered_attacks(self, board: chess.Board, color: chess.Color) -> List[TacticalPattern]:
        """Find discovered attack patterns"""
        patterns = []
        
        # This is complex to implement fully, returning placeholder for now
        # Would need to simulate moving each piece and see if it reveals an attack
        
        return patterns
    
    def _find_trapped_pieces(self, board: chess.Board, color: chess.Color) -> List[TacticalPattern]:
        """Find pieces with no safe moves"""
        patterns = []
        
        # Skip trapped piece detection in opening positions or if too many pieces on starting squares
        piece_count = len(board.piece_map())
        if piece_count >= 30:  # Early game, most pieces still on board
            return patterns
        
        opponent_color = not color
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece or piece.color != opponent_color:
                continue
            
            # Skip checking kings and pawns for trapped pieces
            if piece.piece_type in [chess.KING, chess.PAWN]:
                continue
            
            # Count all legal moves for this piece
            piece_moves = []
            for move in board.legal_moves:
                if move.from_square == square:
                    piece_moves.append(move)
            
            # If piece has no legal moves at all, it's potentially trapped
            if len(piece_moves) == 0:
                continue
            
            # Count safe moves for this piece
            safe_moves = 0
            for move in piece_moves:
                # Check if destination is safe
                board.push(move)
                # Consider a move safe if the piece isn't immediately recaptured
                if not board.is_attacked_by(color, move.to_square):
                    safe_moves += 1
                board.pop()
            
            # Only consider truly trapped if piece has moves but none are safe AND it's in danger
            if safe_moves == 0 and len(piece_moves) > 0 and board.is_attacked_by(color, square):
                severity = "critical" if piece.piece_type in [chess.QUEEN, chess.ROOK] else "major"
                patterns.append(TacticalPattern(
                    name="Trapped Piece",
                    description=f"{piece.symbol().upper()} has no safe moves and is under attack",
                    attacking_square="",
                    target_squares=[chess.square_name(square)],
                    pattern_type="trapped_piece",
                    severity=severity,
                    emoji="🕳️"
                ))
        
        return patterns
    
    def _find_double_attacks(self, board: chess.Board, color: chess.Color) -> List[TacticalPattern]:
        """Find positions where multiple pieces attack the same target"""
        patterns = []
        
        for target_square in chess.SQUARES:
            target_piece = board.piece_at(target_square)
            if not target_piece or target_piece.color == color:
                continue
            
            # Count how many pieces of 'color' attack this square
            attacking_pieces = []
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece and piece.color == color:
                    if self._piece_attacks_square(board, square, target_square):
                        attacking_pieces.append(square)
            
            if len(attacking_pieces) >= 2:
                # Check if target is inadequately defended
                defenders = self._count_defenders(board, target_square, not color)
                if len(attacking_pieces) > defenders:
                    severity = self._calculate_double_attack_severity(board, target_piece)
                    patterns.append(TacticalPattern(
                        name="Double Attack",
                        description=f"{len(attacking_pieces)} pieces attack {target_piece.symbol().upper()}",
                        attacking_square="",
                        target_squares=[chess.square_name(sq) for sq in attacking_pieces] + [chess.square_name(target_square)],
                        pattern_type="double_attack",
                        severity=severity,
                        emoji="⚔️"
                    ))
        
        return patterns
    
    def _piece_attacks_square(self, board: chess.Board, from_square: int, to_square: int) -> bool:
        """Check if piece on from_square attacks to_square"""
        piece = board.piece_at(from_square)
        if not piece:
            return False
        
        # Use board's attack detection
        attacks = board.attacks(from_square)
        return to_square in attacks
    
    def _get_piece_directions(self, piece_type: int) -> List[Tuple[int, int]]:
        """Get movement directions for sliding pieces"""
        if piece_type == chess.ROOK:
            return [(0, 1), (0, -1), (1, 0), (-1, 0)]
        elif piece_type == chess.BISHOP:
            return [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        elif piece_type == chess.QUEEN:
            return [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        return []
    
    def _find_pin_in_direction(self, board: chess.Board, start_square: int, direction: Tuple[int, int], color: chess.Color) -> Tuple[Optional[int], Optional[int]]:
        """Find pin pattern in specific direction"""
        dx, dy = direction
        start_file, start_rank = chess.square_file(start_square), chess.square_rank(start_square)
        
        pinned_piece = None
        valuable_piece = None
        
        file, rank = start_file + dx, start_rank + dy
        
        while 0 <= file <= 7 and 0 <= rank <= 7:
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece:
                if piece.color != color:  # Enemy piece
                    if pinned_piece is None:
                        pinned_piece = square
                    elif valuable_piece is None and piece.piece_type > chess.PAWN:
                        valuable_piece = square
                        break
                    else:
                        break
                else:  # Friendly piece blocks the line
                    break
            
            file += dx
            rank += dy
        
        # Valid pin: enemy piece pinned to a more valuable enemy piece
        if pinned_piece and valuable_piece:
            pinned = board.piece_at(pinned_piece)
            valuable = board.piece_at(valuable_piece)
            if valuable.piece_type > pinned.piece_type:
                return pinned_piece, valuable_piece
        
        return None, None
    
    def _find_skewer_in_direction(self, board: chess.Board, start_square: int, direction: Tuple[int, int], color: chess.Color) -> Tuple[Optional[int], Optional[int]]:
        """Find skewer pattern in specific direction"""
        dx, dy = direction
        start_file, start_rank = chess.square_file(start_square), chess.square_rank(start_square)
        
        front_piece = None
        back_piece = None
        
        file, rank = start_file + dx, start_rank + dy
        
        while 0 <= file <= 7 and 0 <= rank <= 7:
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece and piece.color != color:  # Enemy piece
                if front_piece is None:
                    front_piece = square
                elif back_piece is None:
                    back_piece = square
                    break
            elif piece:  # Friendly piece blocks
                break
            
            file += dx
            rank += dy
        
        # Valid skewer: more valuable piece in front, less valuable behind
        if front_piece and back_piece:
            front = board.piece_at(front_piece)
            back = board.piece_at(back_piece)
            if front.piece_type > back.piece_type:
                return front_piece, back_piece
        
        return None, None
    
    def _count_defenders(self, board: chess.Board, square: int, color: chess.Color) -> int:
        """Count how many pieces defend a square"""
        defenders = 0
        for defender_square in chess.SQUARES:
            piece = board.piece_at(defender_square)
            if piece and piece.color == color:
                if self._piece_attacks_square(board, defender_square, square):
                    defenders += 1
        return defenders
    
    def _calculate_fork_severity(self, board: chess.Board, target_squares: List[int]) -> str:
        """Calculate severity of fork based on target values"""
        total_value = 0
        for square in target_squares:
            piece = board.piece_at(square)
            if piece:
                total_value += self._get_piece_value(piece.piece_type)
        
        if total_value >= 15:  # Queen + Rook or similar
            return "critical"
        elif total_value >= 8:  # Rook + Minor piece
            return "major"
        else:
            return "minor"
    
    def _calculate_pin_severity(self, board: chess.Board, valuable_square: int) -> str:
        """Calculate severity based on the valuable piece being pinned"""
        piece = board.piece_at(valuable_square)
        if piece:
            if piece.piece_type == chess.KING:
                return "critical"
            elif piece.piece_type == chess.QUEEN:
                return "major"
            else:
                return "minor"
        return "minor"
    
    def _calculate_skewer_severity(self, board: chess.Board, front_square: int, back_square: int) -> str:
        """Calculate skewer severity"""
        front_piece = board.piece_at(front_square)
        back_piece = board.piece_at(back_square)
        
        if front_piece and back_piece:
            front_value = self._get_piece_value(front_piece.piece_type)
            back_value = self._get_piece_value(back_piece.piece_type)
            
            if front_value >= 9:  # Queen being skewered
                return "critical"
            elif front_value >= 5:  # Rook being skewered
                return "major"
            else:
                return "minor"
        
        return "minor"
    
    def _calculate_double_attack_severity(self, board: chess.Board, target_piece: chess.Piece) -> str:
        """Calculate double attack severity"""
        value = self._get_piece_value(target_piece.piece_type)
        if value >= 9:
            return "critical"
        elif value >= 5:
            return "major"
        else:
            return "minor"
    
    def _get_piece_value(self, piece_type: int) -> int:
        """Get standard piece values"""
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 100
        }
        return values.get(piece_type, 0)

# Global instance
tactical_analyzer = TacticalAnalyzer()