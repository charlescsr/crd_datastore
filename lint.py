from pylint.lint import Run

results = Run(['app.py'], do_exit=False)

print(results.linter.stats['global_note'])