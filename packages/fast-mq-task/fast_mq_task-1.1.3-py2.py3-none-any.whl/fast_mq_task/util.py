def ref_to_obj(ref):
    """
    将包与路径引用串反序列化成可执行对象
    Returns the object pointed to by ``ref``.
    :type ref: str
    """
    if not isinstance(ref, str):
        raise TypeError('References must be strings')
    if ':' not in ref:
        raise ValueError('Invalid reference')

    module_name, rest = ref.split(':', 1)
    try:
        obj = __import__(module_name, fromlist=[rest])
    except ImportError:
        raise LookupError('Error resolving reference %s: could not import module' % ref)

    try:
        for name in rest.split('.'):
            obj = getattr(obj, name)
        return obj
    except Exception:
        raise LookupError('Error resolving reference %s: error looking up object' % ref)
