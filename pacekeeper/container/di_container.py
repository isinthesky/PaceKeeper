# container/di_container.py

import inspect
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar('T')


class DIContainer:
    """
    의존성 주입 컨테이너

    서비스들의 등록, 해결, 생명주기 관리를 담당합니다.
    싱글톤과 트랜지언트(일회성) 라이프사이클을 지원합니다.
    """

    def __init__(self) -> None:
        self._services: dict[type, tuple] = {}
        self._singletons: dict[type, Any] = {}

    def register_singleton(self, interface: type[T], implementation: type[T] | Callable[[], T]) -> None:
        """
        싱글톤으로 서비스 등록

        Args:
            interface: 인터페이스 또는 추상 클래스
            implementation: 구현 클래스 또는 팩토리 함수
        """
        self._services[interface] = ('singleton', implementation)

    def register_transient(self, interface: type[T], implementation: type[T] | Callable[[], T]) -> None:
        """
        트랜지언트(매번 새 인스턴스)로 서비스 등록

        Args:
            interface: 인터페이스 또는 추상 클래스
            implementation: 구현 클래스 또는 팩토리 함수
        """
        self._services[interface] = ('transient', implementation)

    def register_instance(self, interface: type[T], instance: T) -> None:
        """
        기존 인스턴스를 싱글톤으로 등록

        Args:
            interface: 인터페이스 또는 추상 클래스
            instance: 등록할 인스턴스
        """
        self._services[interface] = ('singleton', lambda: instance)
        self._singletons[interface] = instance

    def resolve(self, interface: type[T]) -> T:
        """
        등록된 서비스를 해결하여 인스턴스 반환

        Args:
            interface: 해결할 인터페이스

        Returns:
            해결된 서비스 인스턴스

        Raises:
            ValueError: 등록되지 않은 서비스인 경우
        """
        if interface not in self._services:
            raise ValueError(f"Service not registered: {interface}")

        lifecycle, implementation = self._services[interface]

        if lifecycle == 'singleton':
            if interface not in self._singletons:
                self._singletons[interface] = self._create_instance(implementation)
            return self._singletons[interface]
        else:  # transient
            return self._create_instance(implementation)

    def _create_instance(self, implementation: type | Callable) -> Any:
        """
        구현체로부터 인스턴스 생성

        Args:
            implementation: 구현 클래스 또는 팩토리 함수

        Returns:
            생성된 인스턴스
        """
        if callable(implementation) and not inspect.isclass(implementation):
            # 팩토리 함수인 경우
            return implementation()

        # 클래스인 경우 생성자 의존성 자동 주입
        return self._create_with_dependencies(implementation)

    def _create_with_dependencies(self, cls: type) -> Any:
        """
        생성자 의존성을 자동으로 주입하여 인스턴스 생성

        Args:
            cls: 생성할 클래스

        Returns:
            의존성이 주입된 인스턴스
        """
        # 생성자 시그니처 분석
        signature = inspect.signature(cls.__init__)
        dependencies = {}

        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue

            # 타입 어노테이션이 있는 경우 해당 타입으로 의존성 해결
            if param.annotation != inspect.Parameter.empty:
                dependencies[param_name] = self.resolve(param.annotation)
            elif param.default == inspect.Parameter.empty:
                raise ValueError(f"Cannot resolve dependency: {param_name} in {cls}")

        return cls(**dependencies)

    def is_registered(self, interface: type) -> bool:
        """
        서비스가 등록되어 있는지 확인

        Args:
            interface: 확인할 인터페이스

        Returns:
            등록 여부
        """
        return interface in self._services

    def clear(self) -> None:
        """
        모든 등록된 서비스와 싱글톤 인스턴스 제거
        """
        self._services.clear()
        self._singletons.clear()
