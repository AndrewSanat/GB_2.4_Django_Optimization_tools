import datetime

import requests
from social_core.exceptions import AuthForbidden

from authapp.models import ShopUserProfile


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name != 'vk-oauth2':
        return

    # api_url = urlunparse(('https',
    #                       'api.vk.com',
    #                       '/method/users.get',
    #                       None,
    #                       urlencode(OrderedDict(fields=','.join(('bdate', 'sex',
    #                                                              'about')),
    #                                             access_token=response['access_token'],
    #                                             v='5.92')),
    #                       None
    #                       ))

    api_url = f'https://api.vk.com/method/users.get/?fields=bdate,sex,about&access_token={response["access_token"]}&v=5.92'

    response = requests.get(api_url)

    if response.status_code != 200:
        return

    data = response.json()['response'][0]

    if 'sex' in data:
        if data['sex'] == 1:
            user.shopuserprofile.gender = ShopUserProfile.FEMALE
        elif data['sex'] == 2:
            user.shopuserprofile.gender = ShopUserProfile.MALE

    if 'about' in data:
        user.shopuserprofile.about_me = data['about']

    if 'bdate' in data:
        bdate = datetime.strptime(data['bdate'], "%d.%m.%Y")
        age = datetime.now().year - bdate.year
        if age < 18:
            user.delete()
            raise AuthForbidden('social_core.backends.vk.VKOAuth2')
        user.age = age

    user.save()