import datetime
from uuid import uuid4

from django.utils.timezone import now
from factory import (
    Faker,
    LazyFunction,
    Sequence,
    SubFactory,
    fuzzy,
    post_generation,
)
from factory.django import DjangoModelFactory

from wind_for_life.apps.anemometers.models import (
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
    Anemometer,
    Reading,
)

TAG_CHOICES = [
    "gusty",
    "breezy",
    "calm",
    "blustery",
    "strong",
    "light",
    "turbulent",
    "whistling",
    "howling",
    "steady",
    "variable",
    "chilly",
    "dry",
    "moist",
    "gentle",
    "fierce",
    "biting",
    "persistent",
    "brisk",
    "stormy",
    "drafty",
    "swirling",
    "squally",
    "whipping",
    "mild",
]


class AnemometerFactory(DjangoModelFactory):
    """Anemometer factory used for tests and population

    To create a batch with readings do the following:
    AnemometerFactory.create_batch(
        number_of_anemometers,
        readings=number_of_readings_per_anemometers
    )
    """

    class Meta:  # type: ignore  # noqa: PGH003
        model = Anemometer

    id = LazyFunction(uuid4)
    name = Sequence(lambda n: f"Anemometer{n}")
    latitude = fuzzy.FuzzyDecimal(
        low=MIN_LATITUDE,
        high=MAX_LATITUDE,
        precision=6,
    )
    longitude = fuzzy.FuzzyDecimal(
        low=MIN_LONGITUDE,
        high=MAX_LONGITUDE,
        precision=6,
    )

    @post_generation
    def readings(self, create, extracted, **kwargs):
        """
        Automatically create readings when an Anemometer is created.

        Args:
            create (bool): Whether the object has been created.
            extracted (int or list): Number of readings or a list of readings to create.
        """
        if not create:
            return

        if extracted:
            if isinstance(extracted, int):
                if extracted < 0:
                    msg = "Cannot have a negative number of readings"
                    raise ValueError(
                        msg,
                    )
                readings = ReadingFactory.create_batch(
                    extracted,
                    anemometer=self,
                )
                for reading in readings:
                    # Model._after_postgeneration will stop saving the instance after postgeneration hooks in the next major release.  # noqa: E501
                    reading.save()
            elif isinstance(extracted, list):
                for reading in extracted:
                    reading.anemometer = self
                    reading.save()


class ReadingFactory(DjangoModelFactory):
    class Meta:  # type: ignore  # noqa: PGH003
        model = Reading

    id = LazyFunction(uuid4)
    speed = Faker("pyfloat", left_digits=3, right_digits=3, positive=True)
    recorded_at = fuzzy.FuzzyDateTime(
        now() - datetime.timedelta(days=7),
        now(),
    )
    anemometer = SubFactory(AnemometerFactory)

    # NOTE: tags post_generation hook removed - was causing infinite loops
    # Tags are still available on the model but not auto-created in tests
