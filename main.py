from shelf_stocker import ShelfStocker

# Continuously gather reddit data and upload to database
def main():
    while True:
        stocker = ShelfStocker()
        stocker.get_new_submissions()
        stocker.update_old_submissions()


if __name__ == '__main__':
    main()
