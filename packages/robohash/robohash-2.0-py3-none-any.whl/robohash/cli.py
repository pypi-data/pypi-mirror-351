import argparse
import io
import sys
from typing import NoReturn
from robohash import Robohash


def main() -> NoReturn:
    """
    Command-line interface for Robohash.
    Parses arguments and generates a robot image based on input text.
    """
    parser = argparse.ArgumentParser(description="Generate a robot hash image from text input")
    parser.add_argument("-s", "--set", default="set1", help="Robot set to use (set1, set2, set3, set4, set5, or 'any')")
    parser.add_argument("-x", "--width", type=int, default=300, help="Width of output image")
    parser.add_argument("-y", "--height", type=int, default=300, help="Height of output image")
    parser.add_argument("-f", "--format", default="png", help="Output format (png, jpeg, etc.)")
    parser.add_argument("-b", "--bgset", help="Background set to use (bg1, bg2, or 'any')")
    parser.add_argument("-o", "--output", default="robohash.png", help="Output filename")
    parser.add_argument("text", help="Text to use for the hash")
    
    args = parser.parse_args()
    
    robohash = Robohash(args.text)
    robohash.assemble(
        roboset=args.set,
        bgset=args.bgset,
        sizex=args.width,
        sizey=args.height,
        format=args.format
    )
    
    robohash.img.save(args.output, format=args.format)
    sys.exit(0)

if __name__ == "__main__":
    main()
