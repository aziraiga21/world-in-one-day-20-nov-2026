"""Copy the rendered front page to the grader's output directory."""
import os
from pathlib import Path
from shutil import copyfile


if __name__ == '__main__':
    source = Path(__file__).resolve().with_name('entry.png')
    output = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', 'output'))
    output.mkdir(parents=True, exist_ok=True)
    target = output / source.name
    if target.resolve() != source and not (target.exists() and target.samefile(source)):
        copyfile(source, target)
