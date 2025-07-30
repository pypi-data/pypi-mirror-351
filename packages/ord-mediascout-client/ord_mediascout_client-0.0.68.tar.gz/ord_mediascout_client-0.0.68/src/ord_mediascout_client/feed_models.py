from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from .models import (
    CampaignType,
    CreativeForm,
    CreativeMediaDataItem,
    CreateCreativeMediaDataItem,
    CreateCreativeTextDataItem,
    CreativeTextDataItemWebApiDto,
    EditCreativeMediaDataItem,
    EditCreativeTextDataItem,
    ErirValidationError,
    TargetAudienceParam,
    capitalize
)


class FeedStatus(Enum):
    Creating = 'Creating'
    MediaDownloadError = 'MediaDownloadError'
    Created = 'Created'
    RegistrationRequired = 'RegistrationRequired'
    Registering = 'Registering'
    Active = 'Active'
    RegistrationError = 'RegistrationError'
    DeletionRequired = 'DeletionRequired'
    Deleting = 'Deleting'
    DeletionError = 'DeletionError'
    Deleted = 'Deleted'


class ElementFeedStatusEnum(Enum):
    Pending = 'Pending'  # Добавлен в очередь и ожидает загрузки внешних файлов
    Downloading = 'Downloading'  # Внешние файлы скачиваются
    Downloaded = 'Downloaded'  # Добавление медиаданных к элементам фидов в ОРД
    Failed = 'Failed'  # Ошибка создания
    WaitingForRetry = 'WaitingForRetry'  # Ожидает повторной отправки
    RegistrationRequired = 'RegistrationRequired'  # ожидает регистрации в ЕРИР
    Registering = 'Registering'  # в процессе регистрации в ЕРИР
    Active = 'Active'  # активный. Зарегистрирован в ЕРИР
    RegistrationError = 'RegistrationError'  # ошибка регистрации в ЕРИР
    ReadyToDownload = 'ReadyToDownload'
    DeletionRequired = 'DeletionRequired'
    Deleting = 'Deleting'
    DeletionError = 'DeletionError'
    Deleted = 'Deleted'
    Duplicate = 'Duplicate'


class TargetAudienceParams(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    geo: Optional[str] = None


class AdvertisementStatusResponse(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    status: FeedStatus = Field(
        ...,
        description='Статус рекламного элемента<p>Members:</p>'
                    '<ul><li><i>Creating</i> - Идет загрузка в ОРД (элемент фида создан, но медиа-данные еще не загружены)</li>'
                    '<li><i>Created</i> - Создан в БД (наша валидация пройдена). Пока не используется, сущность сразу переходит в статус [Ожидает регистрации].</li>'
                    '<li><i>RegistrationRequired</i> - Ожидает регистрации в ЕРИР</li>'
                    '<li><i>Registering</i> - Идет регистрация, быстрый контроль ЕРИР пройден, ждем уточненного ответа</li>'
                    '<li><i>Active</i> - Активный</li>'
                    '<li><i>RegistrationError</i> - Ошибка регистрации ЕРИР (любого этапа)</li>'
                    '<li><i>DeletionRequired</i> - Ожидает удаления в ЕРИР</li>'
                    '<li><i>Deleting</i> - Идет удаление, быстрый контроль ЕРИР пройден, ждем уточненного ответа</li>'
                    '<li><i>DeletionError</i> - Ошибка удаления в ЕРИР (любого этапа)</li>'
                    '<li><i>Deleted</i> - Удален в ЕРИР</li></ul>',
    )


class CreateAdvertisingContainerRequest(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedId: Optional[str] = Field(None, description='Id фида')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    finalContractId: str = Field(..., description='Id доходного договора')
    initialContractId: Optional[str] = Field(
        None,
        description='Id или Cid изначального договора. В случае, если контейнер добавляется только к доходному договору, должно быть NULL.',
    )
    name: str = Field(..., description='Наименование контейнера')
    cobrandingContractIds: Optional[List[str]] = Field(
        None,
        description='Id или Cid совместных договоров\r\n<p style="color: blue">Поле условно-обязательно для заполнения. Обязательно, если `IsCobranding`=`true`</p>',
    )
    isCobranding: bool = Field(
        ...,
        description='Признак совместной рекламы\r\n<p style="color: lightblue">Поле не обязательно для заполнения. Если не заполнено, устанавливается значение `false`</p>',
    )
    nativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id контейнера')
    type: CampaignType = Field(
        ...,
        description='Тип рекламной кампании<p>Members:</p><ul><li><i>CPM</i> - Cost Per Millennium, оплата за тысячу показов</li><li><i>CPC</i> - Cost Per Click, оплата за клик баннера</li><li><i>CPA</i> - Cost Per Action, оплата за совершенное целевое действие</li><li><i>Other</i> - Иное</li></ul>',
    )
    form: CreativeForm = Field(
        ...,
        description='Форма распространения рекламы<p>Members:</p><ul><li><i>Banner</i> - Баннер</li><li><i>Text</i> - Текстовый блок</li><li><i>TextGraphic</i> - Текстово-графический блок</li><li><i>Video</i> - Видеоролик</li><li><i>Audio</i> - Аудиозапись</li><li><i>AudioBroadcast</i> - Аудиотрансляции в прямом эфире</li><li><i>VideoBroadcast</i> - Видеотрансляции в прямом эфире</li><li><i>Other</i> - Иное - не поддерживается начиная с ЕРИР v.5</li><li><i>TextVideoBlock</i> - Текстовый блок с видео</li><li><i>TextAudioBlock</i> - Текстовый блок с аудио</li><li><i>TextAudioVideoBlock</i> - Текстовый блок с аудио и видео</li><li><i>TextGraphicVideoBlock</i> - Текстово-графический блок с видео</li><li><i>TextGraphicAudioBlock</i> - Текстово-графический блок с аудио</li><li><i>TextGraphicAudioVideoBlock</i> - Текстово-графический блок с аудио и видео</li><li><i>BannerHtml5</i> - HTML5-баннер</li></ul>',
    )
    targetAudienceParams: Optional[List[TargetAudienceParam]] = Field(
        None, description='Параметры целевой аудитории рекламы'
    )
    description: str = Field(..., description='Общее описание объекта рекламирования')
    isNative: bool = Field(..., description='Признак нативной рекламы')
    isSocial: bool = Field(..., description='Признак социальной рекламы')
    isSocialQuota: bool = Field(
        ..., description='Признак социальной рекламы по квоте\r\n           <p style=\"color: lightblue\">Поле не обязательно для заполнения. Если не заполнено, устанавливается значение `false`</p>'
    )
    kktuCodes: Optional[List[str]] = Field(
        None,
        description="Список кодов ККТУ. Возможные значения кодов ККТУ можно получить через метод `/webapi/v3/dictionaries/kktu`.\r\nДопускаются только коды 3 уровня - \"X.X.X\"",
        example=['30.1.2', '12.2.3']
    )


class AdvertisingContainerResponse(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedId: Optional[str] = Field(None, description='Id фида')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    finalContractId: str = Field(..., description='Id доходного договора')
    initialContractId: Optional[str] = Field(
        None,
        description='Id или Cid изначального договора. В случае, если контейнер добавляется только к доходному договору, должно быть NULL.',
    )
    cobrandingContractIds: Optional[List[str]] = Field(
        None,
        description='Id или Cid совместных договоров\r\n<p style="color: blue">Поле условно-обязательно для заполнения. Обязательно, если `IsCobranding`=`true`</p>',
    )
    name: str = Field(..., description='Наименование контейнера')
    nativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id контейнера')
    type: Optional[CampaignType] = Field(
        None,
        description='Тип рекламной кампании\r\n<p style="color: lightblue">Поле не обязательно для заполнения. Обязательно, если не будет заполняться аналогичное поле `Type` при регистрации статистики показов контейнера</p><p>Members:</p><ul><li><i>CPM</i> - Cost Per Millennium, оплата за тысячу показов</li><li><i>CPC</i> - Cost Per Click, оплата за клик баннера</li><li><i>CPA</i> - Cost Per Action, оплата за совершенное целевое действие</li><li><i>Other</i> - Иное</li></ul>',
    )
    form: CreativeForm = Field(
        ...,
        description='Форма распространения рекламы<p>Members:</p><ul><li><i>Banner</i> - Баннер</li><li><i>Text</i> - Текстовый блок</li><li><i>TextGraphic</i> - Текстово-графический блок</li><li><i>Video</i> - Видеоролик</li><li><i>Audio</i> - Аудиозапись</li><li><i>AudioBroadcast</i> - Аудиотрансляции в прямом эфире</li><li><i>VideoBroadcast</i> - Видеотрансляции в прямом эфире</li><li><i>TextVideoBlock</i> - Текстовый блок с видео</li><li><i>TextAudioBlock</i> - Текстовый блок с аудио</li><li><i>TextAudioVideoBlock</i> - Текстовый блок с аудио и видео</li><li><i>TextGraphicVideoBlock</i> - Текстово-графический блок с видео</li><li><i>TextGraphicAudioBlock</i> - Текстово-графический блок с аудио</li><li><i>TextGraphicAudioVideoBlock</i> - Текстово-графический блок с аудио и видео</li><li><i>BannerHtml5</i> - HTML5-баннер</li></ul>',
    )
    targetAudienceParams: Optional[List[TargetAudienceParam]] = Field(
        None, description='Параметры целевой аудитории рекламы'
    )
    description: Optional[str] = Field(
        None,
        description='Общее описание объекта рекламирования\r\n<p style="color: blue">Поле условно-обязательно для заполнения. Обязательно для кода ККТУ `30.15.1`</p>',
    )
    isNative: bool = Field(
        ...,
        description='Признак нативной рекламы (Данное поле будет игнорироваться с 01.04.2025 и будет удалено 01.07.2025)',
    )
    isSocialQuota: bool = Field(
        ...,
        description='Признак социальной рекламы по квоте\r\n           <p style="color: lightblue">Поле не обязательно для заполнения. Если не заполнено, устанавливается значение `false`</p>',
    )
    isSocial: bool = Field(..., description='Признак социальной рекламы')
    isCobranding: bool = Field(
        ...,
        description='Признак совместной рекламы\r\n<p style="color: lightblue">Поле не обязательно для заполнения. Если не заполнено, устанавливается значение `false`</p>',
    )
    kktuCodes: List[str] = Field(
        ...,
        description='Список кодов ККТУ. Возможные значения кодов ККТУ можно получить через метод `/webapi/v3/dictionaries/kktu`.\r\nДопускаются только коды 3 уровня - "X.X.X"\r\n<p style="color: blue">Поле обязательно для заполнения</p>',
        example=['30.1.2', '12.2.3'],
    )
    id: str = Field(..., description='Id контейнера')
    erid: str = Field(..., description='Erid контейнера')
    status: FeedStatus = Field(
        ...,
        description='Статус контейнера<p>Members:</p><ul><li><i>Creating</i> - Идет загрузка в ОРД (элемент фида создан, но медиа-данные еще не загружены)</li><li><i>MediaDownloadError</i> - Не удалось скачать медифайл для элемента фида (пока используется только для элементов фидов)</li><li><i>Created</i> - Создан в БД (наша валидация пройдена). Пока не используется, сущность сразу переходит в статус [Ожидает регистрации].</li><li><i>RegistrationRequired</i> - Ожидает регистрации в ЕРИР</li><li><i>Registering</i> - Идет регистрация, быстрый контроль ЕРИР пройден, ждем уточненного ответа</li><li><i>Active</i> - Активный</li><li><i>RegistrationError</i> - Ошибка регистрации ЕРИР (любого этапа)</li><li><i>DeletionRequired</i> - Ожидает удаления в ЕРИР</li><li><i>Deleting</i> - Идет удаление, быстрый контроль ЕРИР пройден, ждем уточненного ответа</li><li><i>DeletionError</i> - Ошибка удаления в ЕРИР (любого этапа)</li><li><i>Deleted</i> - Удален в ЕРИР</li></ul>',
    )
    feedName: Optional[str] = Field(None, description='Наименование фида')
    erirValidationError: Optional[ErirValidationError] = None


class GetContainerWebApiDto(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    id: Optional[str] = None
    nativeCustomerId: Optional[str] = None
    erid: Optional[str] = None
    feedNativeCustomerId: Optional[str] = None
    initialContractId: Optional[str] = None
    initialContractNumber: Optional[str] = None
    finalContractId: Optional[str] = None
    finalContractNumber: Optional[str] = None
    status: Optional[FeedStatus] = None


class EditAdvertisingContainerRequest(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedId: Optional[str] = Field(None, description='Id фида')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    finalContractId: str = Field(..., description='Id доходного договора')
    initialContractId: Optional[str] = Field(
        None,
        description='Id или Cid изначального договора. В случае, если контейнер добавляется только к доходному договору, должно быть NULL.',
    )
    name: str = Field(..., description='Наименование контейнера')
    cobrandingContractIds: Optional[List[str]] = Field(
        None,
        description='Id или Cid совместных договоров\r\n<p style="color: blue">Поле условно-обязательно для заполнения. Обязательно, если `IsCobranding`=`true`</p>',
    )
    isCobranding: bool = Field(
        ...,
        description='Признак совместной рекламы\r\n<p style="color: lightblue">Поле не обязательно для заполнения. Если не заполнено, устанавливается значение `false`</p>',
    )
    nativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id контейнера')
    type: CampaignType = Field(
        ...,
        description='Тип рекламной кампании<p>Members:</p><ul><li><i>CPM</i> - Cost Per Millennium, оплата за тысячу показов</li><li><i>CPC</i> - Cost Per Click, оплата за клик баннера</li><li><i>CPA</i> - Cost Per Action, оплата за совершенное целевое действие</li><li><i>Other</i> - Иное</li></ul>',
    )
    form: CreativeForm = Field(
        ...,
        description='Форма распространения рекламы<p>Members:</p><ul><li><i>Banner</i> - Баннер</li><li><i>Text</i> - Текстовый блок</li><li><i>TextGraphic</i> - Текстово-графический блок</li><li><i>Video</i> - Видеоролик</li><li><i>Audio</i> - Аудиозапись</li><li><i>AudioBroadcast</i> - Аудиотрансляции в прямом эфире</li><li><i>VideoBroadcast</i> - Видеотрансляции в прямом эфире</li><li><i>TextVideoBlock</i> - Текстовый блок с видео</li><li><i>TextAudioBlock</i> - Текстовый блок с аудио</li><li><i>TextAudioVideoBlock</i> - Текстовый блок с аудио и видео</li><li><i>TextGraphicVideoBlock</i> - Текстово-графический блок с видео</li><li><i>TextGraphicAudioBlock</i> - Текстово-графический блок с аудио</li><li><i>TextGraphicAudioVideoBlock</i> - Текстово-графический блок с аудио и видео</li><li><i>BannerHtml5</i> - HTML5-баннер</li></ul>',
    )
    targetAudienceParams: Optional[List[TargetAudienceParam]] = Field(
        None, description='Параметры целевой аудитории рекламы'
    )
    description: str = Field(..., description='Общее описание объекта рекламирования')
    isNative: bool = Field(..., description='Признак нативной рекламы')
    isSocial: bool = Field(..., description='Признак социальной рекламы')
    isSocialQuota: bool = Field(
        ..., description='Признак социальной рекламы по квоте\r\n           <p style=\"color: lightblue\">Поле не обязательно для заполнения. Если не заполнено, устанавливается значение `false`</p>'
    )
    kktuCodes: Optional[List[str]] = Field(
        None,
        description='Список кодов ККТУ. Возможные значения кодов ККТУ можно получить через метод `/webapi/v3/dictionaries/kktu`.\r\nДопускаются только коды 3 уровня - "X.X.X"',
        example=['30.1.2', '12.2.3'],
    )
    id: Optional[str] = Field(None, description='Id контейнера')
    erid: Optional[str] = Field(None, description='Erid контейнера')


class FeedElementTextDataItem(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    id: Optional[str] = None
    textData: Optional[str] = None


class CreateFeedElement(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    nativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id элемента фида')
    description: str = Field(..., description='Общее описание объекта рекламирования')
    advertiserUrls: List[str] = Field(
        ..., description='Целевые ссылки (сайты рекламодателя, на который осуществляется переход по клику на рекламе)'
    )
    mediaData: Optional[List[CreateCreativeMediaDataItem]] = Field(
        None, description='Медиаданные элемента фида (массив)'
    )
    textData: Optional[List[CreateCreativeTextDataItem]] = Field(
        None, description='Текстовые медиаданные элемента фида (массив)'
    )


class EditDelayedFeedElement(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    id: Optional[str] = Field(None, description='Id элемента фида')
    nativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id элемента фида')
    description: str = Field(..., description='Общее описание объекта рекламирования')
    advertiserUrls: List[str] = Field(
        ..., description='Целевые ссылки (сайты рекламодателя, на который осуществляется переход по клику на рекламе)'
    )
    overwriteExistingCreativeMedia: bool = Field(
        ...,
        description='Перезаписать все предыдущие медиаданные элемента фида (файловые и текстовые). Токен останется прежним, существующие медиаданные удалятся, переданные медиаданые запишутся.\r\n<p style="color: lightblue">Поле не обязательно для заполнения. Если не заполнено, устанавливается значение `false`</p>',
    )
    mediaData: Optional[List[EditCreativeMediaDataItem]] = Field(None, description='Медиаданные элемента фида (массив)')
    textData: Optional[List[EditCreativeTextDataItem]] = Field(
        None, description='Текстовые медиаданные элемента фида (массив)'
    )
    feedId: Optional[str] = Field(None, description='Id фида')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    feedName: Optional[str] = Field(None, description='Наименование фида')


class EditDelayedFeedElementsBulkRequest(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedElements: List[EditDelayedFeedElement]


class EditFeedElementWebApiDto(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    id: Optional[str] = Field(None, description='Id элемента фида')
    nativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id элемента фида')
    description: str = Field(..., description='Общее описание объекта рекламирования')
    advertiserUrls: List[str] = Field(
        ..., description='Целевые ссылки (сайты рекламодателя, на который осуществляется переход по клику на рекламе)'
    )
    overwriteExistingCreativeMedia: bool = Field(
        ...,
        description='Перезаписать все предыдущие медиаданные элемента фида (файловые и текстовые). Токен останется прежним, существующие медиаданные удалятся, переданные медиаданые запишутся.\r\n<p style="color: lightblue">Поле не обязательно для заполнения. Если не заполнено, устанавливается значение `false`</p>',
    )
    mediaData: Optional[List[EditCreativeMediaDataItem]] = Field(None, description='Медиаданные элемента фида (массив)')
    textData: Optional[List[EditCreativeTextDataItem]] = Field(
        None, description='Текстовые медиаданные элемента фида (массив)'
    )


class EditFeedElementsRequest(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedId: Optional[str] = Field(None, description='Id фида')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    feedName: Optional[str] = Field(
        None,
        description='Наименование фида для его создания, а если фид уже существует, и имеет другое наименование, оно будет заменено этим значением',
    )
    feedElements: List[EditFeedElementWebApiDto] = Field(
        ..., description='Список элементов, содержащих индивидуальную информацию для каждого элемента фида'
    )


class CreateFeedElementsRequest(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedId: Optional[str] = Field(None, description='Id фида')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    feedName: Optional[str] = Field(
        None,
        description='Наименование фида для его создания, а если фид уже существует, и имеет другое наименование, оно будет заменено этим значением',
    )
    feedElements: List[CreateFeedElement] = Field(
        ..., description='Список элементов, содержащих индивидуальную информацию для каждого элемента фида'
    )


class FeedElementResponse(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    id: str = Field(..., description='Id элемента фида')
    feedId: str = Field(..., description='Id фида')
    feedName: str = Field(..., description='Наименование фида')
    status: FeedStatus = Field(
        ...,
        description='Статус<p>Members:</p><ul><li><i>Creating</i> - Идет загрузка в ОРД (элемент фида создан, но медиа-данные еще не загружены)</li><li><i>Created</i> - Создан в БД (наша валидация пройдена). Пока не используется, сущность сразу переходит в статус [Ожидает регистрации].</li><li><i>RegistrationRequired</i> - Ожидает регистрации в ЕРИР</li><li><i>Registering</i> - Идет регистрация, быстрый контроль ЕРИР пройден, ждем уточненного ответа</li><li><i>Active</i> - Активный</li><li><i>RegistrationError</i> - Ошибка регистрации ЕРИР (любого этапа)</li><li><i>DeletionRequired</i> - Ожидает удаления в ЕРИР</li><li><i>Deleting</i> - Идет удаление, быстрый контроль ЕРИР пройден, ждем уточненного ответа</li><li><i>DeletionError</i> - Ошибка удаления в ЕРИР (любого этапа)</li><li><i>Deleted</i> - Удален в ЕРИР</li></ul>',
    )
    description: str = Field(..., description='Общее описание объекта рекламирования')
    advertiserUrls: List[str] = Field(
        ..., description='Целевые ссылки (сайты рекламодателя, на который осуществляется переход по клику на рекламе)'
    )
    nativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id элемента фида')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    erirValidationError: Optional[ErirValidationError] = None
    mediaData: List[CreativeMediaDataItem] = Field(..., description='Файловые медиаданные элемента фида')
    textData: List[CreativeTextDataItemWebApiDto] = Field(..., description='Текстовые медиаданные элемента фида')


class GetFeedElementsWebApiDto(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    ids: Optional[list[str]] = None
    nativeCustomerId: Optional[str] = None
    feedNativeCustomerId: Optional[str] = None
    status: Optional[str] = None


class DelayedAdvertisementMedia(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    srcUrl: str = Field(..., description='Путь до внешнего файла')
    fileName: str = Field(..., description='Имя файла')
    mediaDownloadError: Optional[str] = Field(None, description='Ошибка загруки внешнего файла')


class DelayedFeedElement(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedElementId: Optional[str] = Field(None, description='Id созданного элемента фида')
    feedElementNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id элемента фида')
    feedId: Optional[str] = Field(None, description='Id фида')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    erirValidationError: Optional[ErirValidationError] = None
    status: ElementFeedStatusEnum = Field(..., description='Статус заявки')
    failedDownloadAttemptCount: Optional[int] = Field(None, description='Количество неудачных попыток скачивания')
    feedElementCreatingErrors: List[str] = Field(
        None, description='Ошибки создания элемента фида (ФЛК, неверные идентификаторы договора и пр)'
    )
    feedElementMedias: List[DelayedAdvertisementMedia] = Field(
        ..., description='Медиа-файлы, необходимые для создания элемента фида'
    )


class CreateDelayedFeedElement(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    nativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id элемента фида')
    description: str = Field(..., description='Общее описание объекта рекламирования')
    advertiserUrls: List[str] = Field(
        ..., description='Целевые ссылки (сайты рекламодателя, на который осуществляется переход по клику на рекламе)'
    )
    mediaData: Optional[List[CreateCreativeMediaDataItem]] = Field(
        None, description='Медиаданные элемента фида (массив)'
    )
    textData: Optional[List[CreateCreativeTextDataItem]] = Field(
        None, description='Текстовые медиаданные элемента фида (массив)'
    )
    feedId: Optional[str] = Field(None, description='Id фида (не заполняется, если фид еще только предстоит создать)')
    feedNativeCustomerId: Optional[str] = Field(None, description='Пользовательский Id фида')
    feedName: Optional[str] = Field(
        None,
        description='Наименование фида для его создания, а если фид уже существует, и имеет другое наименование, оно будет заменено этим значением',
    )


class CreateDelayedFeedElementsBulkRequest(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedElements: List[CreateDelayedFeedElement]


class GetFeedElementsBulkInfo(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    Id: Optional[str] = None
    Status: Optional[ElementFeedStatusEnum] = None


class DelayedFeedElementsBatchInfoResponse(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = capitalize
        allow_population_by_field_name = True

    feedElements: List[DelayedFeedElement] = Field(
        ..., description='Список заявок на отложенное создание элементов фидов'
    )
