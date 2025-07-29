from __future__ import annotations
from typing import TYPE_CHECKING, Type, Callable, Union, Any, TypeVar, Literal, cast
from factory.declarations import LazyFunction
from factory.faker import Faker
import exrex  # type: ignore
from django.db import models
from django.core.validators import RegexValidator
from factory.django import DjangoModelFactory
import random
from decimal import Decimal
from general_manager.measurement.measurement import Measurement
from general_manager.measurement.measurementField import MeasurementField
from datetime import date, datetime, time, timezone

if TYPE_CHECKING:
    from general_manager.interface.databaseInterface import (
        DBBasedInterface,
    )

modelsModel = TypeVar("modelsModel", bound=models.Model)


class AutoFactory(DjangoModelFactory[modelsModel]):
    """
    A factory class that automatically generates values for model fields,
    including handling of unique fields and constraints.
    """

    interface: Type[DBBasedInterface]
    _adjustmentMethod: (
        Callable[..., Union[dict[str, Any], list[dict[str, Any]]]] | None
    ) = None

    @classmethod
    def _generate(
        cls, strategy: Literal["build", "create"], params: dict[str, Any]
    ) -> models.Model | list[models.Model]:
        cls._original_params = params
        model = getattr(cls._meta, "model")
        if not issubclass(model, models.Model):
            raise ValueError("Model must be a type")
        field_name_list, to_ignore_list = cls.interface.handleCustomFields(model)

        fields = [
            field
            for field in model._meta.get_fields()
            if field.name not in to_ignore_list
        ]
        special_fields: list[models.Field[Any, Any]] = [
            getattr(model, field_name) for field_name in field_name_list
        ]
        pre_declations = getattr(cls._meta, "pre_declarations", [])
        post_declarations = getattr(cls._meta, "post_declarations", [])
        declared_fields: set[str] = set(pre_declations) | set(post_declarations)

        field_list: list[models.Field[Any, Any] | models.ForeignObjectRel] = [
            *fields,
            *special_fields,
        ]

        for field in field_list:
            if field.name in [*params, *declared_fields]:
                continue  # Skip fields that are already set
            if isinstance(field, models.AutoField) or field.auto_created:
                continue  # Skip auto fields
            params[field.name] = getFieldValue(field)

        obj: list[models.Model] | models.Model = super()._generate(strategy, params)
        if isinstance(obj, list):
            for item in obj:  # type: ignore
                if not isinstance(item, models.Model):
                    raise ValueError("Model must be a type")
                cls._handleManyToManyFieldsAfterCreation(item, params)
        else:
            cls._handleManyToManyFieldsAfterCreation(obj, params)
        return obj

    @classmethod
    def _handleManyToManyFieldsAfterCreation(
        cls, obj: models.Model, attrs: dict[str, Any]
    ) -> None:
        for field in obj._meta.many_to_many:
            if field.name in attrs:
                m2m_values = attrs[field.name]
            else:
                m2m_values = getManyToManyFieldValue(field)
            if m2m_values:
                getattr(obj, field.name).set(m2m_values)

    @classmethod
    def _adjust_kwargs(cls, **kwargs: dict[str, Any]) -> dict[str, Any]:
        # Remove ManyToMany fields from kwargs before object creation
        model: Type[models.Model] = getattr(cls._meta, "model")
        m2m_fields = {field.name for field in model._meta.many_to_many}
        for field_name in m2m_fields:
            kwargs.pop(field_name, None)
        return kwargs

    @classmethod
    def _create(
        cls, model_class: Type[models.Model], *args: list[Any], **kwargs: dict[str, Any]
    ) -> models.Model | list[models.Model]:
        kwargs = cls._adjust_kwargs(**kwargs)
        if cls._adjustmentMethod is not None:
            return cls.__createWithGenerateFunc(strategy=True, params=kwargs)
        return cls._modelCreation(model_class, **kwargs)

    @classmethod
    def _build(
        cls, model_class: Type[models.Model], *args: list[Any], **kwargs: dict[str, Any]
    ) -> models.Model | list[models.Model]:
        kwargs = cls._adjust_kwargs(**kwargs)
        if cls._adjustmentMethod is not None:
            return cls.__createWithGenerateFunc(strategy=False, params=kwargs)
        return cls._modelBuilding(model_class, **kwargs)

    @classmethod
    def _modelCreation(
        cls, model_class: Type[models.Model], **kwargs: dict[str, Any]
    ) -> models.Model:
        obj = model_class()
        for field, value in kwargs.items():
            setattr(obj, field, value)
        obj.full_clean()
        obj.save()
        return obj

    @classmethod
    def _modelBuilding(
        cls, model_class: Type[models.Model], **kwargs: dict[str, Any]
    ) -> models.Model:
        obj = model_class()
        for field, value in kwargs.items():
            setattr(obj, field, value)
        return obj

    @classmethod
    def __createWithGenerateFunc(
        cls, strategy: bool, params: dict[str, Any]
    ) -> models.Model | list[models.Model]:
        model_cls = getattr(cls._meta, "model")
        if cls._adjustmentMethod is None:
            raise ValueError("generate_func is not defined")
        records = cls._adjustmentMethod(**params)
        if isinstance(records, dict):
            if strategy:
                return cls._modelCreation(model_cls, **records)
            return cls._modelBuilding(model_cls, **records)

        created_objects: list[models.Model] = []
        for record in records:
            if strategy:
                created_objects.append(cls._modelCreation(model_cls, **record))
            else:
                created_objects.append(cls._modelBuilding(model_cls, **record))
        return created_objects


def getFieldValue(field: models.Field[Any, Any] | models.ForeignObjectRel) -> object:
    """
    Returns a suitable value for a given Django model field.
    """
    if field.null:
        if random.choice([True] + 9 * [False]):
            return None

    if isinstance(field, MeasurementField):

        def _measurement():
            value = Decimal(random.randrange(0, 10_000_000)) / Decimal("100")  # two dp
            return Measurement(value, field.base_unit)

        return LazyFunction(_measurement)
    elif isinstance(field, models.TextField):
        return cast(str, Faker("paragraph"))
    elif isinstance(field, models.IntegerField):
        return cast(int, Faker("random_int"))
    elif isinstance(field, models.DecimalField):
        max_digits = field.max_digits
        decimal_places = field.decimal_places
        left_digits = max_digits - decimal_places
        return cast(
            Decimal,
            Faker(
                "pydecimal",
                left_digits=left_digits,
                right_digits=decimal_places,
                positive=True,
            ),
        )
    elif isinstance(field, models.FloatField):
        return cast(float, Faker("pyfloat", positive=True))
    elif isinstance(field, models.DateTimeField):
        return cast(
            datetime,
            Faker(
                "date_time_between",
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            ),
        )
    elif isinstance(field, models.DateField):
        return cast(date, Faker("date_between", start_date="-1y", end_date="today"))
    elif isinstance(field, models.BooleanField):
        return cast(bool, Faker("pybool"))
    elif isinstance(field, models.OneToOneField):
        if hasattr(field.related_model, "_general_manager_class"):
            related_factory = field.related_model._general_manager_class.Factory
            return related_factory()
        else:
            # If no factory exists, pick a random existing instance
            related_instances = list(field.related_model.objects.all())
            if related_instances:
                return LazyFunction(lambda: random.choice(related_instances))
            else:
                raise ValueError(
                    f"No factory found for {field.related_model.__name__} and no instances found"
                )
    elif isinstance(field, models.ForeignKey):
        # Create or get an instance of the related model
        if hasattr(field.related_model, "_general_manager_class"):
            create_a_new_instance = random.choice([True, True, False])
            if not create_a_new_instance:
                existing_instances = list(field.related_model.objects.all())
                if existing_instances:
                    # Pick a random existing instance
                    return LazyFunction(lambda: random.choice(existing_instances))

            related_factory = field.related_model._general_manager_class.Factory
            return related_factory()

        else:
            # If no factory exists, pick a random existing instance
            related_instances = list(field.related_model.objects.all())
            if related_instances:
                return LazyFunction(lambda: random.choice(related_instances))
            else:
                raise ValueError(
                    f"No factory found for {field.related_model.__name__} and no instances found"
                )
    elif isinstance(field, models.EmailField):
        return cast(str, Faker("email"))
    elif isinstance(field, models.URLField):
        return cast(str, Faker("url"))
    elif isinstance(field, models.GenericIPAddressField):
        return cast(str, Faker("ipv4"))
    elif isinstance(field, models.UUIDField):
        return cast(str, Faker("uuid4"))
    elif isinstance(field, models.DurationField):
        return cast(time, Faker("time_delta"))
    elif isinstance(field, models.CharField):
        max_length = field.max_length or 100
        # Check for RegexValidator
        regex = None
        for validator in field.validators:
            if isinstance(validator, RegexValidator):
                regex = getattr(validator.regex, "pattern", None)
                break
        if regex:
            # Use exrex to generate a string matching the regex
            return LazyFunction(lambda: exrex.getone(regex))  # type: ignore
        else:
            return cast(str, Faker("text", max_nb_chars=max_length))
    else:
        return None  # For unsupported field types


def getManyToManyFieldValue(
    field: models.ManyToManyField,
) -> list[models.Model]:
    """
    Returns a list of instances for a ManyToMany field.
    """
    related_factory = None
    related_instances = list(field.related_model.objects.all())
    if hasattr(field.related_model, "_general_manager_class"):
        related_factory = field.related_model._general_manager_class.Factory

    min_required = 0 if field.blank else 1
    number_of_instances = random.randint(min_required, 10)
    if related_factory and related_instances:
        number_to_create = random.randint(min_required, number_of_instances)
        number_to_pick = number_of_instances - number_to_create
        if number_to_pick > len(related_instances):
            number_to_pick = len(related_instances)
        existing_instances = random.sample(related_instances, number_to_pick)
        new_instances = [related_factory() for _ in range(number_to_create)]
        return existing_instances + new_instances
    elif related_factory:
        number_to_create = number_of_instances
        new_instances = [related_factory() for _ in range(number_to_create)]
        return new_instances
    elif related_instances:
        number_to_create = 0
        number_to_pick = number_of_instances
        if number_to_pick > len(related_instances):
            number_to_pick = len(related_instances)
        existing_instances = random.sample(related_instances, number_to_pick)
        return existing_instances
    else:
        raise ValueError(
            f"No factory found for {field.related_model.__name__} and no instances found"
        )
