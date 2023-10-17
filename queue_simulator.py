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

        # queue2
        self.queue2 = 0
        self.times2 = [0,0,0,0,0]
        self.loss2 = 0

        self.__argument_parsing()

        self.arrival(3.0)

        while self.iterations > 0:
            next_event = self.scheduler.pop(0)
            if next_event.event_type == 'arrival':
                self.arrival(next_event.time)
            elif next_event.event_type == 'passage':
                self.passage_event(next_event.time)
            else:
                self.exit(next_event.time)

        # all valeu with 4 decimal places
        self.times = [round(time, 4) for time in self.times]
        self.times2 = [round(time, 4) for time in self.times2]

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
                           self.random_between(self.min_service2, self.max_service2))
        self.insert_event(exit_event)

    def exit(self, time):
        self.times[self.queue] += (time - self.global_time)
        self.times2[self.queue2] += (time - self.global_time)
        self.global_time = time

        self.queue2 -= 1
        if self.queue2 >= self.number_servers2:
            self.exit_schedule()

    def arrival_schedule(self):
        entry_event = Event('arrival', self.global_time +
                            self.random_between(self.min_arrival, self.max_arrival))
        self.insert_event(entry_event)

    def arrival(self, time):
        self.times[self.queue] += (time - self.global_time)
        self.times2[self.queue2] += (time - self.global_time)
        self.global_time = time

        if self.queue < self.capacity:
            self.queue += 1
            if self.queue <= self.number_servers:
                self.passage_schedule()
        else:
            self.loss += 1
        self.arrival_schedule()

    def passage_schedule(self):
        passage_event = Event('passage', self.global_time +
                              self.random_between(self.min_service, self.max_service))
        self.insert_event(passage_event)

    def passage_event(self, time):
        self.times[self.queue] += (time - self.global_time)
        self.times2[self.queue2] += (time - self.global_time)
        self.global_time = time
        self.queue -= 1
        if self.queue >= self.number_servers:
            self.passage_schedule()
        if self.queue2 < self.capacity2:
            self.queue2 += 1
            if self.queue2 <= self.number_servers2:
                self.exit_schedule()
        else:
            self.loss2 += 1


    def __argument_parsing(self):
        """! ArgumentParser routine"""
        parser = argparse.ArgumentParser(usage='python3 queue_simulator.py -a 1 3 -s 2 4 -n 1 -c 5',
                                         description='Queue simulator')
        parser.add_argument('-a', '--average-arrival',
                            nargs='+', type=int, help='Average arrival time')
        parser.add_argument('-s', '--average-service',
                            nargs='+', type=int, help='Average service time for queue 1 and 2')
        parser.add_argument('-n', '--number-servers', nargs='+',
                            type=int, help='Number of servers for queue 1 and 2')
        parser.add_argument('-c', '--capacity', nargs='+', type=int,
                            help='Capacity of the queue 1 and 2')

        args = parser.parse_args()

        self.min_arrival = args.average_arrival[0]
        self.max_arrival = args.average_arrival[1]
        self.min_service = args.average_service[0]
        self.max_service = args.average_service[1]
        self.number_servers = args.number_servers[0]
        self.capacity = args.capacity[0]
        self.times = [0] * (self.capacity + 1)

        self.min_service2 = args.average_service[2]
        self.max_service2 = args.average_service[3]
        self.capacity2 = args.capacity[1]
        self.number_servers2 = args.number_servers[1]


def main():
    queues = [QueueSimulator(10), QueueSimulator(209), QueueSimulator(666), QueueSimulator(5024),
              QueueSimulator(9999)]

    i = 1
    for queue in queues:
        print('Iteration: {}'.format(i))
        print(' Queue 1 times: {}'.format(queue.times))
        print(' loss queue 1: {}'.format(queue.loss))
        print()
        print(' Queue 2 times: {}'.format(queue.times2))
        print(' loss queue 2: {}'.format(queue.loss2))
        print()
        print(' Total time: {}'.format(round(queue.global_time, 4)))
        print('=' * 50)
        i += 1

    average_times = [0] * (queues[0].capacity + 1)
    for i in range(len(average_times)):
        for queue in queues:
            average_times[i] += queue.times[i]
            average_times[i] = round((average_times[i] / len(queues)), 4)

    average_times2 = [0] * (queues[0].capacity2 + 1)
    for i in range(len(average_times2)):
        for queue in queues:
            average_times2[i] += queue.times2[i]
            average_times2[i] = round((average_times2[i] / len(queues)), 4)

    print('Average time queue 1: {}'.format(average_times))
    print('Average time queue 2: {}'.format(average_times2))
    print('Average total time: {}'.format(round(sum(average_times), 4)))


if __name__ == '__main__':
    main()
