from typing import Optional, List
import aiohttp
from pydantic import ValidationError

from aioallay.types import *


class Client:
    base_url = "https://api.mblueberry.fun"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    async def get_user(self, user_id: int) -> User | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/{user_id}", headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                return User(**data)

    async def get_user_roles(self, user_id: int) -> list[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/{user_id}/roles", headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                return data

    async def get_all_user(self) -> List[User]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/all", headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                users = [User(**user_data) for user_data in data]
                return users

    async def update_game_profiler(self, old_xbox: str, new_xbox: str) -> bool:
        async with aiohttp.ClientSession() as session:

            async with session.get(f"{self.base_url}/users/update-gp/{old_xbox}/{new_xbox}",
                                   headers=self.headers) as response:
                if response.status >= 404:
                    return False
                return True

    async def update_user(self, user_id: int, edit_type: str, value: str) -> List[User]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/{user_id}/update/{edit_type}/{value}",
                                   headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                data = await response.json()
                return User(**data)

    async def find_users(self, value: str) -> List[User]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/find?value={value}", headers=self.headers) as response:
                if response.status == 404:
                    return None
                if response.status == 204:
                    return None
                if response.status == 200:
                    response.raise_for_status()
                    data = await response.json()
                    users = [User(**user_data) for user_data in data]
                    return users

    async def get_top_time(self, page: int, count: int, period: str) -> Optional[List[UserTime]]:
        params = {"page": page, "count": count, "period": period}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/stata/game-time", headers=self.headers, params=params) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                users = [UserTime(**user_data) for user_data in data]
                return users

    async def get_all_simple_market(self) -> List[SimpleMarket]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/simple-market", headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                print(data)

                market = [SimpleMarket(**market_data) for market_data in data]
                return market

    async def delete_simple_market(self, user_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/simple-market/{user_id}", headers=self.headers) as response:

                if response.status == 200:
                    return True
                else:
                    return False

    async def create_simple_market(self, market_data: MarketItem) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.base_url}/simple-market",
                    json=market_data.dict(),
                    headers=self.headers) as response:

                if response.status == 200:
                    return True
                else:
                    return False

    async def get_top_donate(self, ) -> List[Donate]:
        url = f"{self.base_url}/stata/donate/top"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                donates = [Donate(**donate_data) for donate_data in data]
                return donates

    async def get_top_rate(self, page: int, count: int) -> List[RateTop]:

        params = {"page": page, "count": count}
        url = f"{self.base_url}/stata/rate/top"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                donates = [RateTop(**rate_data) for rate_data in data]
                return donates

    async def get_top_rate_user(self, page: int, count: int) -> List[Rate]:
        url = f"{self.base_url}/users/rate"
        params = {"page": page, "count": count}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                users_data = data.get("content", [])
                users = [User(**user_data) for user_data in users_data]
                return users

    async def get_top_updays_users(self, page: int, count: int) -> Optional[List[User]]:
        url = f"{self.base_url}/users/updays"
        params = {"page": page, "count": count}  # Передача параметрів запиту
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                users_data = data.get("content", [])
                users = [User(**user_data) for user_data in users_data]
                return users

    async def get_birthday_today(self) -> Optional[List[User]]:
        url = f"{self.base_url}/users/birthday-today"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()

                print(data)
                data = await response.json()
                users = [User(**user_data) for user_data in data]
                return users

    async def get_upcome_bday(self) -> Optional[List[User]]:
        url = f"{self.base_url}/users/birthday-upcoming"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()

                print(data)
                data = await response.json()
                users = [User(**user_data) for user_data in data]
                return users

    async def set_bio(self, user_id: int, bio: str) -> Optional[User]:
        url = f"{self.base_url}/users/bio"
        json = {"user_id": user_id, "bio": bio}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=self.headers, json=json
            ) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()

                return User(**data)

    async def upload_pack(
        self, file_path: str, icon_path: str, name: str, description: str, author: str
    ):
        url = f"{self.base_url}/pack"

        # Create FormData object to handle file uploads
        form_data = aiohttp.FormData()
        form_data.add_field(
            "file",
            open(file_path, "rb"),
            filename="file.zip",
            content_type="application/zip",
        )
        form_data.add_field(
            "icon", open(icon_path, "rb"), filename="icon.png", content_type="image/png"
        )
        form_data.add_field("name", name)
        form_data.add_field("description", description)
        form_data.add_field("author", author)

        # Send the POST request with form data
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=self.headers, data=form_data
            ) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                return await response.json()

    async def reset_password(self, username: str, password: str) -> Optional[dict]:
        url = f"{self.base_url}/users/resetpass"
        params = {
            "username": username,
            "password": password
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                return User(**data)

    async def has_allow_cmd(self, telegram_id: int, cmd: str) -> bool:
        url = f"{self.base_url}/command/user/{telegram_id}/{cmd}"
        print(url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                print(response.status)
                if response.status >= 404:
                    return False
                if response.status >= 200:
                    return True

    async def create_role(self, role: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/command/role/{role}", headers=self.headers) as response:
                if response.status >= 404:
                    return False
                return True

    async def create_cmd(self, cmd: str, description: str, cmd_type: str) -> bool:
        json = {
            "command": cmd,
            "description": description,
            "type": cmd_type,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/command/cmd", headers=self.headers, json=json) as response:
                if response.status >= 404:
                    return False
                return True

    async def add_role_to_cmd(self, cmd: str, role: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/command/cmd/{cmd}/{role}", headers=self.headers) as response:
                if response.status >= 404:
                    return False
                return True

    async def enable_user(self, user_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/enable/{user_id}",
                                    headers=self.headers) as response:
                if response.status >= 404:
                    return False
                return True
    async def delete_user(self, user_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/delete/{user_id}",
                                    headers=self.headers) as response:
                if response.status >= 404:
                    return False
                return True

    async def add_role_to_user(self, role: str, telegram_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/command/user/{telegram_id}/{role}",
                                    headers=self.headers) as response:
                if response.status >= 404:
                    return False
                return True

    async def get_all_commands(self) -> List[Command]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/command", headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()

                data = await response.json()
                users = [Command(**user_data) for user_data in data]
                return users

    async def get_bank_card(self, card_id: int) -> User | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/bank/{card_id}", headers=self.headers) as response:
                print(response.status)
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                print(data)
                return BankCard(**data)

    async def add_rate(self, rate: RateRequest) -> Rate:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/stata/rate", json=rate.model_dump(), headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                return Rate(**data)

    async def get_user_rates(self, user_id: int, page: int, count: int) -> Optional[List[User]]:
        url = f"{self.base_url}/stata/rate/user/{user_id}"
        params = {"page": page, "count": count}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                users = [Rate(**user_data) for user_data in data]
                return users


    async def auth_by_key(self, user_id: int, key: str) -> User | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/auth/{user_id}/{key}",headers=self.headers) as response:
                response.raise_for_status()

    async def get_user_by_tg(self, telegram_id: int) -> User | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/tg?telegram_id={telegram_id}",
                                   headers=self.headers) as response:
                print(response.status)
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                print(data)
                return User(**data)

    async def get_user_by_xbox(self, xbox: str) -> User | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/xbox/{xbox}",
                                   headers=self.headers) as response:
                print(response.status)
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()

                return User(**data)

    async def get_user_donate(self, telegram_id: int) -> List[Donate] | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/stata/donate/user/{telegram_id}",
                                   headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                return [Donate(**donate_data) for donate_data in data]

    async def get_stata_block(self, xbox: str) -> List[BlockStata] | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/stata/block/{xbox}",
                                   headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                return [BlockStata(**block_data) for block_data in await response.json()]

    async def set_donate(self, money, user_id) -> bool:
        json = {
            "user_id": user_id,
            "money": money
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.base_url}/stata/donate",  # Заміни на реальний URL
                    json=json,
                    headers=self.headers) as response:
                if response.status == 200:
                    return True
                else:
                    return False
    async def create_gp(self,user_id:int, xbox: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.base_url}/game-profile/user/{user_id}/{xbox}",
                    headers=self.headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                return GameProfile(**data)

    async def add_message_stata(self, message: str, telegram_id: int) -> bool:
        json = {
            "message": message,
            "type": "tg",
            "telegram_id": telegram_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.base_url}/stata/message/tg",  # Заміни на реальний URL
                    json=json,
                    headers=self.headers) as response:
                if response.status == 200:
                    return True
                else:
                    return False

    async def get_top_message_stata(self, page: int, count: int, period: str = "all") -> List[UserMessageStata]:
        params = {"page": page, "count": count, "period": period}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/stata/message/top",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    try:
                        response.raise_for_status()
                        data = await response.json()
                        print(data)
                        return [ UserMessageStata(**msg) for msg in data["content"] ]
                    except ValidationError as e:
                        print(f"Pydantic validation error: {e}")
                        return None
                return None

    async def create_profile(self, profile_data: NewProfileRequest):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.base_url}/users",  # Заміни на реальний URL
                    json=profile_data.model_dump(),
                    headers=self.headers) as response:
                # Отримуємо відповідь
                if response.status == 200:
                    # result = await response.json()
                    print("Success")
                else:
                    print("Failed:", response.status)

    async def upload_image(self, file_path: str) -> None:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as file:
                # Використовуйте aiohttp для відправки файлу
                form_data = aiohttp.FormData()
                form_data.add_field('file', file, filename=file_path.split('/')[-1])

                async with session.post(f"{self.base_url}/upload/image", headers=self.headers,
                                        data=form_data) as response:
                    response.raise_for_status()  # Піднімає виключення для статусів помилок
                    if response.status == 200:
                        print("File uploaded successfully")
                    else:
                        print("Failed to upload file:", await response.text())

    async def update_user_rate(self, user_id: int, rate):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/add_rate/{user_id}/{rate}",
                                   headers=self.headers) as response:
                print(response.status)
                if response.status == 404:
                    return None
                response.raise_for_status()  # Це підніме виключення для інших статусів помилок
                data = await response.json()
                return User(**data)

    async def gat_stata_block_page(self, xbox: str, event: str, page: int, size: int) -> Page[BlockStata]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/stata/block/{xbox}/{event}/paged?page={page}&size={size}",
                    headers=self.headers
            ) as response:
                data = await response.json()
                return Page[BlockStata](**data)

    async def get_stata_ate_page(self, xbox: str, page: int, size: int) -> Page[AteStata]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/stata/ate/{xbox}/paged?page={page}&size={size}",
                    headers=self.headers
            ) as response:
                data = await response.json()
                return Page[AteStata](**data)

    async def get_stata_fish_page(self, xbox: str, page: int, size: int) -> Page[FishStata]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/stata/fish/{xbox}/paged?page={page}&size={size}",
                    headers=self.headers
            ) as response:
                data = await response.json()
                return Page[FishStata](**data)

    async def get_stata_mobs_page(self, xbox: str, page: int, size: int) -> Page[MobsStata]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/stata/mobs/{xbox}/paged?page={page}&size={size}",
                    headers=self.headers
            ) as response:
                data = await response.json()
                return Page[MobsStata](**data)

    async def get_base_stata(self, xbox: str) -> BaseStata:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/stata/base/{xbox}",
                    headers=self.headers
            ) as response:
                data = await response.json()
                return BaseStata(**data)

    async def get_all_server(self) -> List[Server]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/server", headers=self.headers) as response:
                data = await response.json()
                return [Server(**server) for server in data]

    async def get_server(self, server_id: int) -> Server:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/server/{server_id}", headers=self.headers) as response:
                data = await response.json()
                return Server(**data)

    async def update_server(self, server: Server) -> Server:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/server/edit",
                json=server.model_dump(),
                headers=self.headers,
            ) as response:
                data = await response.json()
                return Server(**data)

    async def get_android_allay_version(self) -> AllayVersion:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/allay/android/latest",
                headers=self.headers,
            ) as response:
                data = await response.json()
                return AllayVersion(**data)

    async def get_windows_allay_version(self) -> AllayVersion:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/allay/windows/latest",
                headers=self.headers,
            ) as response:
                data = await response.json()
                return AllayVersion(**data)

    async def get_all_city_orders(self) -> List[CityOrder]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/city_order", headers=self.headers) as response:
                data = await response.json()
                return [CityOrder(**city_order) for city_order in data]



    async def take_city_order(self, user_id: int, order_id: int) -> TakeCityOrderResponse:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/city_order/take/{user_id}/{order_id}", headers=self.headers) as response:

                code = response.status == 200
                message = await response.text()
                order_response = TakeCityOrderResponse(ok = code, message=message)
                print(order_response.model_dump())
                return order_response

