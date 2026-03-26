from VK.VK_Bot import VKbot_class
from tokens import vk_token


def main():
    vkbot = VKbot_class(vk_token)
    vkbot.event_handler()


if __name__ == '__main__':
    main()

