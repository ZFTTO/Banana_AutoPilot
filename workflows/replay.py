"""Replay a recorded session: python -m workflow.replay --session datasets/session_001."""

from __future__ import annotations

import argparse
import csv
import math
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecordedFrame:
    image_path: Path
    timestamp: float
    throttle: float
    steering: float


def load_session(session_path: Path) -> list[RecordedFrame]:
    """Load labels in recording order and validate their referenced images."""
    frames = []
    images_directory = (session_path / "images").resolve()
    with (session_path / "labels.csv").open(newline="", encoding="utf-8-sig") as labels:
        reader = csv.DictReader(labels)
        required_columns = {"image", "timestamp", "throttle", "steering"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError("labels.csv requires image, timestamp, throttle and steering columns")

        for line_number, row in enumerate(reader, start=2):
            try:
                image_path = (images_directory / row["image"]).resolve()
                frame = RecordedFrame(
                    image_path=image_path,
                    timestamp=float(row["timestamp"]),
                    throttle=float(row["throttle"]),
                    steering=float(row["steering"]),
                )
            except (ValueError, TypeError) as error:
                raise ValueError(f"Invalid label on CSV line {line_number}") from error
            if not image_path.is_relative_to(images_directory):
                raise ValueError(f"Image on CSV line {line_number} is outside the images directory")
            if not image_path.is_file():
                raise ValueError(f"Missing image: {image_path}")
            if not all(math.isfinite(value) for value in
                       (frame.timestamp, frame.throttle, frame.steering)):
                raise ValueError(f"Non-finite number on CSV line {line_number}")
            if frames and frame.timestamp < frames[-1].timestamp:
                raise ValueError(f"Timestamp goes backwards on CSV line {line_number}")
            frames.append(frame)

    if not frames:
        raise ValueError("The session contains no frames")
    return frames


def replay(session_path: Path, frames: list[RecordedFrame], speed: float) -> None:
    """Play locally; arrow keys step through frames while paused."""
    import pygame

    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 760))
        pygame.display.set_caption(f"Banana AutoPilot Replay - {session_path.name}")
        font = pygame.font.Font(None, 25)
        clock = pygame.time.Clock()
        image_area = pygame.Rect(0, 0, 800, 580)
        timestamps = [frame.timestamp - frames[0].timestamp for frame in frames]
        duration = timestamps[-1]
        playhead = 0.0
        frame_index = 0
        loaded_index = -1
        image = None
        paused = False
        running = True

        while running:
            elapsed = clock.tick(60) / 1000.0
            if not paused:
                playhead = min(duration, playhead + elapsed * speed)
                frame_index = max(0, bisect_right(timestamps, playhead) - 1)
                if playhead >= duration:
                    paused = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if paused and frame_index == len(frames) - 1:
                            frame_index = 0
                            playhead = 0.0
                        paused = not paused
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        paused = True
                        step = -1 if event.key == pygame.K_LEFT else 1
                        frame_index = max(0, min(len(frames) - 1, frame_index + step))
                        playhead = timestamps[frame_index]
                    elif event.key == pygame.K_HOME:
                        frame_index = 0
                        playhead = 0.0
                    elif event.key == pygame.K_UP:
                        speed = min(8.0, speed * 2)
                    elif event.key == pygame.K_DOWN:
                        speed = max(0.125, speed / 2)

            if not running:
                break
            frame = frames[frame_index]
            if frame_index != loaded_index:
                try:
                    source = pygame.image.load(str(frame.image_path)).convert()
                except (pygame.error, OSError) as error:
                    raise ValueError(f"Cannot decode image: {frame.image_path}") from error
                fitted = source.get_rect().fit(image_area)
                image = pygame.transform.smoothscale(source, fitted.size)
                loaded_index = frame_index

            screen.fill((20, 22, 26))
            screen.blit(image, image.get_rect(center=image_area.center))
            status = "PAUSED" if paused else "PLAYING"
            lines = [
                f"{session_path.name} | {status} | {speed:g}x",
                f"Frame {frame_index + 1}/{len(frames)} | {playhead:.2f}s / {duration:.2f}s",
                f"Throttle: {frame.throttle:+.3f}   Steering: {frame.steering:+.3f}",
                "=== Command Hints ===",
                "Space: play/pause   Left/Right: step   Up/Down: speed",
                "Home: rewind   Q/Esc: quit",
            ]
            for line_index, line in enumerate(lines):
                screen.blit(font.render(line, True, (235, 235, 235)),
                            (16, 594 + line_index * 27))
            pygame.display.flip()
    finally:
        pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay recorded images and driving labels locally.")
    parser.add_argument("--session", type=Path, required=True, help="Session directory containing labels.csv and images/")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback multiplier, from 0.125 to 8 (default: 1)")
    args = parser.parse_args()
    if not math.isfinite(args.speed) or not 0.125 <= args.speed <= 8:
        parser.error("--speed must be between 0.125 and 8")
    try:
        frames = load_session(args.session)
        replay(args.session, frames, args.speed)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Replay error: {error}\n")


if __name__ == "__main__":
    main()
