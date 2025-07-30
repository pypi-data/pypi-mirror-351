from datetime import date, datetime, time
from uuid import UUID

from dataclass_parser.examples.entities import (
    Data, DataList, DataOneToOne, DataOneToList, DateTimeEntity, UUIDEntity,
    OptionalValue, UnionValue, Nested, Complex, MixedCollections, StatusEntity,
    Money, FileInfo, MixedCollection, Matrix,
    AdvancedCollections, Recursion, Department, Employee
)


class DataOrm:
    name = 'asd'


class DataListOrm:
    data_list = [DataOrm()]


class DataOneToOneOrm:
    data = DataOrm()


class DataOneToListOrm:
    data_list = [DataListOrm()]


class DataDatetimeOrm:
    created_at = datetime.now()


class DataUUIDOrm:
    id = UUID('90fcc034-063c-4064-8632-df43219ce405')


class DataOptionalOrm:
    value = None


class DataUnionOrm:
    value = 'test'


class DataNestedOrm:
    timestamp = datetime.now()
    items = [DataUUIDOrm(), DataUUIDOrm()]
    metadata = {'version': 1, 'status': 'active'}


class DataComplexOrm:
    created_at = date.today()
    updated_at = time(12, 30, 45)
    versions = (1.0, 2.0, 3.0)
    details = DataNestedOrm()


class DataMixedCollectionsOrm:
    users = {'Alice', 'Bob', 'Charlie'}
    matrix = [[1, 2], [3, 4], [5, 6]]


class StatusOrm:
    value = 'ACTIVE'


class MoneyOrm:
    amount = '100.50'
    currency = 'USD'


class BoxOrm:
    content = 'secret'


class AgeOrm:
    value = 150


class FileInfoOrm:
    path = '/data/test.txt'
    size = 1024


class MixedCollectionOrm:
    items = [1, 'two', 3.0]


class MatrixOrm:
    rows = [[1, 2], [3, 4]]


class OptionalNestedOrm:
    child = None


class AdvancedCollectionsOrm:
    data = {
        'matrix': [[1, 2], [3, 4]],
        'unique': {1, 2, 3},
        'nested': {'a': [{'b': 5}]},
    }


class RecursionOrm:
    data: list['RecursionOrm']

    def __init__(self, depth: int = 0, max_depth: int = 2) -> None:
        if depth < max_depth:
            self.data = [RecursionOrm(depth + 1, max_depth)]
        else:
            self.data = []


class DepartmentOrm:
    employees: list['EmployeeOrm']

    def __init__(self, employees: list['EmployeeOrm'] | None = None) -> None:
        if not employees:
            employees = []
        self.employees = employees


class EmployeeOrm:
    department: DepartmentOrm

    def __init__(self, department: DepartmentOrm = DepartmentOrm()) -> None:
        self.department = department


def main():
    print(Data.parse(DataOrm()))
    print(DataList.parse(DataListOrm()))
    print(DataOneToOne.parse(DataOneToOneOrm()))
    print(DataOneToList.parse(DataOneToListOrm()))
    print(DateTimeEntity.parse(DataDatetimeOrm()))
    print(UUIDEntity.parse(DataUUIDOrm()))
    print(OptionalValue.parse(DataOptionalOrm()))
    print(UnionValue.parse(DataUnionOrm()))
    print(Nested.parse(DataNestedOrm()))
    print(Complex.parse(DataComplexOrm()))
    print(MixedCollections.parse(DataMixedCollectionsOrm()))

    print(StatusEntity.parse(StatusOrm()))
    print(Money.parse(MoneyOrm()))

    print(FileInfo.parse(FileInfoOrm()))
    print(MixedCollection.parse(MixedCollectionOrm()))
    print(Matrix.parse(MatrixOrm()))
    print(AdvancedCollections.parse(AdvancedCollectionsOrm()))
    print(Recursion.parse(RecursionOrm()))

    department = DepartmentOrm()
    employee = EmployeeOrm(department)
    department.employees = [employee]
    print(Department.parse(department))
    print(Employee.parse(employee))


if __name__ == '__main__':
    main()
