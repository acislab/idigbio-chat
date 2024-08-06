def repeat(n):
    print()  # pytest stdout doesn't end on a new line
    for i in range(0, n):
        print(f"  Attempt {i}")
        yield n
