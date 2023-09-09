import argparse


class Event(object):

    def __init__(self, event_type, time):
        self.event_type = event_type
        self.time = time


class QueueSimulator():

    def __init__(self, seed):

        self.min_arrival = None
        self.max_arrival = None
        self.min_service = None
        self.max_service = None
        self.number_servers = None
        self.capacity = None
        self.times = None
        self.loss = 0

        self.global_time = 0
        self.queue = 0
        self.iterations = 100000
        self.scheduler = []
        self.seed = seed

        self.__argument_parsing()

        self.arrival(3.0)

        while self.iterations > 0:
            next_event = self.scheduler.pop(0)
            if next_event.event_type == 'arrival':
                self.arrival(next_event.time)
            else:
                self.exit(next_event.time)

        # all valeu with 4 decimal places
        self.times = [round(time, 4) for time in self.times]

    def insert_event(self, event):
        for i in range(len(self.scheduler)):
            if self.scheduler[i].time > event.time:
                self.scheduler.insert(i, event)
                return
        self.scheduler.append(event)

    def next_random(self):
        self.iterations -= 1

        a = 1103515245
        M = 16777216
        c = 12820163
        self.seed = ((a * self.seed + c) % M)
        return self.seed / M

    def random_between(self, a, b):
        return (b - a) * self.next_random() + a

    def exit_schedule(self):
        exit_event = Event('exit', self.global_time +
                           self.random_between(self.min_service, self.max_service))
        self.insert_event(exit_event)

    def exit(self, time):
        self.times[self.queue] += (time - self.global_time)
        self.global_time = time

        self.queue -= 1
        if self.queue >= self.number_servers:
            self.exit_schedule()

    def arrival_schedule(self):
        entry_event = Event('arrival', self.global_time +
                            self.random_between(self.min_arrival, self.max_arrival))
        self.insert_event(entry_event)

    def arrival(self, time):
        self.times[self.queue] += (time - self.global_time)
        self.global_time = time

        if self.queue < self.capacity:
            self.queue += 1
            if self.queue <= self.number_servers:
                self.exit_schedule()
        else:
            self.loss += 1
        self.arrival_schedule()

    def __argument_parsing(self):
        """! ArgumentParser routine"""
        parser = argparse.ArgumentParser(usage='python3 queue_simulator.py -a 1 3 -s 2 4 -n 1 -c 5',
                                         description='Queue simulator')
        parser.add_argument('-a', '--average-arrival',
                            nargs='+', type=int, help='Average arrival time')
        parser.add_argument('-s', '--average-service',
                            nargs='+', type=int, help='Average service time')
        parser.add_argument('-n', '--number-servers',
                            type=int, help='Number of servers')
        parser.add_argument('-c', '--capacity', type=int,
                            help='Capacity of the queue')

        args = parser.parse_args()

        self.min_arrival = args.average_arrival[0]
        self.max_arrival = args.average_arrival[1]
        self.min_service = args.average_service[0]
        self.max_service = args.average_service[1]
        self.number_servers = args.number_servers
        self.capacity = args.capacity
        self.times = [0] * (self.capacity + 1)


def main():
    queues = [QueueSimulator(10), QueueSimulator(209), QueueSimulator(666), QueueSimulator(5024),
              QueueSimulator(9999)]

    i = 1
    for queue in queues:
        print('Queue :{}'.format(i))
        print(' Times: {}'.format(queue.times))
        print(' Total time: {}'.format(round(queue.global_time, 4)))
        print(' loss: {}'.format(queue.loss))
        print()
        i += 1

    average_times = [0] * (queues[0].capacity + 1)
    for i in range(len(average_times)):
        for queue in queues:
            average_times[i] += queue.times[i]
            average_times[i] = round((average_times[i] / len(queues)), 4)

    print('Average times: {}'.format(average_times))
    print('Average total time: {}'.format(round(sum(average_times), 4)))


if __name__ == '__main__':
    main()
