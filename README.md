# mbserializer

## Summary
mbserializer provides model-based serializer.
It can interconvert between python objects and serialized data such as json, xml and yaml.

## Requirements
##### required
- Python 2.6+ or 3.3+

##### optional
- lxml if using XML serialization
- defusedxml if using XML deserialization
- PyYAML if using YAML serialization and deserialization
- python-dateutil if flexibly parsing string-based datetime
- pytz if using string-based timezone

## Usage

First, create models classes and serializer instance.
```python
from mbserializer import Model, Serializer
from mbserializer.fields import StringElement, DelegateList


class Child(Model):
    __tag__ = 'child'

    name = StringElement()


class Parent(Model):
    __tag__ = 'parent'

    name = StringElement()
    children = DelegateList(Child, nested=True)

serializer = Serializer(Parent)
```

#### Serialization

Prepare serialized instance or dict.
```python
class Object(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

parent = Object(
    name='Son Goku',
    children=(
        Object(
            name='Son Gohan'
        ),
        Object(
            name='Son Goten'
        ),
    )
)
```

JSON:
```python
json_parent = serializer.dumps(parent, data_type='json', indent=2)
print(json_parent)
```
```json
{
  "name": "Son Goku",
  "children": [
    {
      "name": "Son Gohan"
    },
    {
      "name": "Son Goten"
    }
  ]
}
```
XML:
```python
xml_parent = serializer.dumps(parent, data_type='xml', pretty_print=True)
print(xml_parent)
```
```xml
<?xml version='1.0' encoding='utf-8'?>
<parent>
  <name>Son Goku</name>
  <children>
    <child>
      <name>Son Gohan</name>
    </child>
    <child>
      <name>Son Goten</name>
    </child>
  </children>
</parent>
```
YAML:
```python
yaml_parent = serializer.dumps(parent, data_type='yaml')
print(yaml_parent)
```
```yaml
name: Son Goku
children:
- {name: Son Gohan}
- {name: Son Goten}
```
#### Deserialization
Parse string to Entity instance.
```python
print(serializer.loads(json_parent, data_type='json'))
print(serializer.loads(xml_parent, data_type='xml'))
print(serializer.loads(yaml_parent, data_type='yaml'))
```
Result:
```python
Entity({'children': [Entity({'name': 'Son Gohan'}), Entity({'name': 'Son Goten'})], 'name': 'Son Goku'})
Entity({'children': [Entity({'name': 'Son Gohan'}), Entity({'name': 'Son Goten'})], 'name': 'Son Goku'})
Entity({'children': [Entity({'name': 'Son Gohan'}), Entity({'name': 'Son Goten'})], 'name': 'Son Goku'})
```
Entity inherits dict, and it can get values by attribute.
```python
>>> from mbserializer import Entity
>>> entity = Entity({'children': [Entity({'name': 'Son Gohan'}), Entity({'name': 'Son Goten'})], 'name': 'Son Goku'})
>>> entity['children'][0]['name']
'Son Gohan'
>>> entity.children[0].name
'Son Gohan'
```
## License

mbserializer is licensed under [MIT](http://www.opensource.org/licenses/mit-license.php "Read more about the MIT license form").