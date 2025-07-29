from pypushflow import persistence


def actorinfo_filter(info):
    return info


persistence.register_actorinfo_filter(actorinfo_filter)
