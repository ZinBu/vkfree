from stats.logic.vkapi import VkCore


class ServiceVK(VkCore):
    def __init__(self, token):
        self.token = token
