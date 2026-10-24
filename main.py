"""
GeneCraft — Shape Genes. Control Evolution. Build a Living World.
Entry point: python main.py
"""
import sys, os, argparse, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def parse_args():
    p = argparse.ArgumentParser(description="GeneCraft — Evolution Simulation")
    p.add_argument("--debug",      action="store_true", help="Enable debug mode")
    p.add_argument("--fullscreen", action="store_true", help="Start fullscreen")
    p.add_argument("--size",       choices=["small","medium","large"], default=None)
    p.add_argument("--skip-menu",  action="store_true", help="Skip main menu (dev)")
    return p.parse_args()

def main():
    args = parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    from utils.logger import setup_logger
    setup_logger(log_level)
    logger = logging.getLogger("GeneCraft")
    logger.info("=" * 55)
    logger.info("  GeneCraft v1.0.0  — Starting up")
    logger.info("=" * 55)

    from engine.config_manager import ConfigManager
    config = ConfigManager()
    config.load_all()

    if args.debug:      config.set("game.debug_mode", True)
    if args.fullscreen: config.set("window.fullscreen", True)
    if args.size:       config.set("world.default_size", args.size)

    try:
        from engine.game_engine import GameEngine
        engine = GameEngine(config=config, skip_menu=args.skip_menu)
        engine.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt — shutting down.")
        return 0
    except Exception as exc:
        logger.critical("Fatal error: %s", exc, exc_info=True)
        return 1
    finally:
        logger.info("GeneCraft session ended.")

if __name__ == "__main__":
    sys.exit(main())
