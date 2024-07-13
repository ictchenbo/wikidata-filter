from wikidata_filter.iterator.base import JsonIterator


class BufferedWriter(JsonIterator):
    def __init__(self, buffer_size=1000):
        self.buffer = []
        self.buffer_size = buffer_size

    def on_data(self, data: dict or None, *args):
        if not isinstance(data, list):
            self.buffer.append(data)
        else:
            self.buffer.extend(data)
        if len(self.buffer) >= self.buffer_size:
            self.write_batch(self.buffer)
            self.buffer.clear()

        return data

    def write_batch(self, data: list):
        pass

    def on_complete(self):
        if self.buffer:
            self.write_batch(self.buffer)
            self.buffer.clear()
