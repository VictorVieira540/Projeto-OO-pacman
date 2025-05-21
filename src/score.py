import pygame
import json
from typing import List, Dict

class Score:
    def __init__(self) -> None:
        self.current_score = 0
        self.high_scores: List[Dict[str, int]] = []
        self.load_high_scores()
    
    def add_points(self, points: int) -> None:
        """Adiciona pontos ao placar atual"""
        self.current_score += points
    
    def save_score(self, player_name: str) -> None:
        """Salva a pontuação atual nos recordes"""
        self.high_scores.append({
            "name": player_name,
            "score": self.current_score
        })
        # Ordena os recordes por pontuação (maior para menor)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        # Mantém apenas os 10 melhores recordes
        self.high_scores = self.high_scores[:10]
        self.save_high_scores()
    
    def load_high_scores(self) -> None:
        """Carrega os recordes do arquivo"""
        try:
            with open("high_scores.json", "r") as f:
                self.high_scores = json.load(f)
        except FileNotFoundError:
            self.high_scores = []
    
    def save_high_scores(self) -> None:
        """Salva os recordes no arquivo"""
        with open("high_scores.json", "w") as f:
            json.dump(self.high_scores, f)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o placar atual na tela"""
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.current_score}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
    
    def draw_high_scores(self, screen: pygame.Surface) -> None:
        """Desenha a tela de recordes"""
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        
        # Título
        title = font.render("High Scores", True, (255, 255, 255))
        screen.blit(title, (350, 50))
        
        # Lista de recordes
        y = 100
        for i, score in enumerate(self.high_scores, 1):
            text = font.render(f"{i}. {score['name']}: {score['score']}", True, (255, 255, 255))
            screen.blit(text, (300, y))
            y += 40
        
        # Instruções
        text = font.render("Pressione ESPAÇO para voltar", True, (255, 255, 255))
        screen.blit(text, (300, 500)) 