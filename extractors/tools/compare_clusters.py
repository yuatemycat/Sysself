import sys

with open(r'C:\Users\X\.local\bin\claude.exe', 'rb') as f:
    f.seek(131801568 - 100)
    c1 = f.read(500)
    print("Cluster 1 at 131801568:")
    print(repr(c1[:200]))
    print("=" * 60)

    f.seek(249386424 - 100)
    c2 = f.read(500)
    print("Cluster 2 at 249386424:")
    print(repr(c2[:200]))
