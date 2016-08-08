def title_sort(plu_src_list):
    """
    Function to sort a list of videogame titles.

    :param plu_src_list:

    :return:
    """
    lu_dst_list = sorted(plu_src_list, key=lambda u_element: u_element.lower())
    return lu_dst_list