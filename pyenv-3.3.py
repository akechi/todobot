#!/usr/bin/env python3.3

if __name__ == '__main__':
    import sys
    print(sys.version)
    rc = 1
    try:
        import venv
        venv.main()
        rc = 0
    except Exception as e:
        print('Error: %s' % e, file=sys.stderr)
    sys.exit(rc)
