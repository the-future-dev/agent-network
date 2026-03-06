from board import Board
from config import Config
import asyncio

async def main():
    cfg = Config()
    board = Board(cfg.db_path)  # cfg.db_path is "board.db"
    await board.init()          # creates posts/comments/upvotes/seen_posts tables
    await board.close()

if __name__ == "__main__":
    asyncio.run(main())
    