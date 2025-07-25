from drgn.helpers.linux import list_for_each_entry


# Print the information for each entry in the list.
# For example, if the source code in C is:
#     struct my_entry *entry;
#     list_for_each_entry(entry, &mylist, node),
# then using the function as:
#     print_list("struct my_entry", mylist, "node"):

def print_list(struct, llist, field):
    for e in list_for_each_entry(struct, llist.address_of_(), field):
        print(e)
