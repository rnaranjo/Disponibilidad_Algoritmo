def two_highest_keyvalue(dicc):
  dicc_copy = dict(dicc)
  key1 = max(dicc_copy, key=dicc_copy.get)
  del dicc_copy[key1]
  key2 = max(dicc_copy, key=dicc_copy.get)
  return [key1, key2]