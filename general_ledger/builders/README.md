# builders

the idea of the builder pattern is to allow the progressive construction of complex objects. the idea is that you can have a pattern which can be used to produce a variety of representations of the same object.

Here, they are mostly being used (misused?) to wrap the django create method with convenience methods, and to allow creation of objects complete with all their related objects.

The builder object generally implements any atomic methods. using a builder also tries to avoid making customizations to the `save(...)` methods of the models.

