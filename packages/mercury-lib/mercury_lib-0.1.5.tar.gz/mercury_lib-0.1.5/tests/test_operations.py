from mercury.operations.sets import S


def test_set_definition_operations():

    Q = S({"a", "b"}) * S(range(3)) | S({0})

    assert 0 in Q
    assert ("a", 0) in Q
    assert ("b", 2) in Q
