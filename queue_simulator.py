import argparse
import random


class Event(object):

    def __init__(self, event_type, time, queue_source=None, queue_destiny=None):
        self.event_type = event_type
        self.time = time
        self.queue_source = queue_source
        self.queue_destiny = queue_destiny


class Queue():

    def __init__(self):
        self.min_arrival = 0
        self.max_arrival = 0
        self.min_service = 0
        self.max_service = 0
        self.number_servers = 0
        self.capacity = 0
        self.times = None
        self.weights = None
        self.loss = 0
        self.population = 0


class QueueSimulator():

    def __init__(self, seed):
        self.global_time = 0
        self.iterations = 2000
        self.scheduler = []
        self.seed = seed

        self.__argument_parsing()

        self.arrival(self.queues[0], 3.0)

        while self.iterations > 0:
            next_event = self.scheduler.pop(0)
            if next_event.event_type == 'arrival':
                self.arrival(self.queues[0], next_event.time)
            elif next_event.event_type == 'passage':
                self.passage_event(next_event)
            else:
                self.exit(next_event)

        # all valeus with 4 decimal places
        for queue in self.queues:
            queue.times = [round(time, 4) for time in queue.times]

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

    def exit_schedule(self, q_sourc):
        ''' Exit schedule
            q_source: Index of queue source
        '''
        exit_event = Event('exit', self.global_time +
                           self.random_between(self.queues[q_sourc].min_service, self.queues[q_sourc].max_service),
                           queue_source=q_sourc)
        self.insert_event(exit_event)

    def exit(self, event):
        # update queues time
        for queue in self.queues:
            queue.times[queue.population] += (event.time - self.global_time)
        self.global_time = event.time

        queue_source = self.queues[event.queue_source]

        queue_source.population -= 1
        if queue_source.population >= queue_source.number_servers:
            q_dest = self.queues.index(random.choices(self.queues, queue_source.weights)[0])

            if event.queue_source == q_dest:
                self.exit_schedule(event.queue_source)
            else:
                self.passage_schedule(event.queue_source, q_dest)


    def arrival_schedule(self):
        entry_event = Event('arrival', self.global_time +
                            self.random_between(self.queues[0].min_arrival, self.queues[0].max_arrival))
        self.insert_event(entry_event)

    def arrival(self, queue, time):
        # update queues time
        for q in self.queues:
            q.times[q.population] += (time - self.global_time)
        self.global_time = time

        if queue.population < queue.capacity:
            queue.population += 1

            if queue.population <= queue.number_servers:
                q_source = self.queues.index(queue)
                q_dest = self.queues.index(random.choices(self.queues, queue.weights)[0])
                self.passage_schedule(q_source, q_dest)
        else:
            queue.loss += 1
        self.arrival_schedule()

    def passage_schedule(self, q_source, q_dest):
        ''' Passage schedule
            q_source: Index of queue source
            q_dest: Index of queue destiny
        '''
        passage_event = Event('passage', self.global_time +
                              self.random_between(self.queues[q_source].min_service, self.queues[q_source].max_service),
                              queue_source=q_source, queue_destiny=q_dest)
        self.insert_event(passage_event)

    def passage_event(self, event):
        # update queues time
        for queue in self.queues:
            queue.times[queue.population] += (event.time - self.global_time)
        self.global_time = event.time

        queue_source = self.queues[event.queue_source]
        queue_destiny = self.queues[event.queue_destiny]

        queue_source.population -= 1

        if queue_source.population >= queue_source.number_servers:
            q_source = self.queues.index(queue_source)
            q_dest = self.queues.index(random.choices(self.queues, queue_source.weights)[0])
            self.passage_schedule(q_source, q_dest)

        if queue_destiny.population < queue_destiny.capacity:
            queue_destiny.population += 1

            if queue_destiny.population <= queue_destiny.number_servers:
                q_source = self.queues.index(queue_destiny)
                q_dest = self.queues.index(random.choices(self.queues, queue_destiny.weights)[0])
                if q_source == q_dest:
                    print(q_source, q_dest)
                    self.exit_schedule(q_source)
                else:
                    self.passage_schedule(q_source, q_dest)
        else:
            queue_destiny.loss += 1


    def __argument_parsing(self):
        """! ArgumentParser routine"""
        parser = argparse.ArgumentParser(
            usage='python3 queue_simulator.py -q 3 -a 1 4 0 0 0 0 -s 1 2 5 10 10 20 -n 1 3 2 -c 100 5 8 -w 0 0.8 0.2 0.3 0.2 0.5 0 0.7 0.3',
            description='Queue simulator'
        )
        parser.add_argument('-q', '--number_of_queues', type=int, help='Number of queues.')
        parser.add_argument('-a', '--average-arrival',
                            nargs='+', type=int, help='Average arrival time.')
        parser.add_argument('-s', '--average-service',
                            nargs='+', type=int, help='Average service time for queue 1 and 2.')
        parser.add_argument('-n', '--number-servers', nargs='+',
                            type=int, help='Number of servers for queue 1 and 2.')
        parser.add_argument('-c', '--capacity', nargs='+', type=int,
                            help='Capacity of the queue 1 and 2.')
        parser.add_argument('-w', '--weights', nargs='+', type=float,
                            help='Weights of outputs.')

        args = parser.parse_args()

        self.queues = [Queue() for _ in range(args.number_of_queues)]

        k = 0
        for i in range(len(self.queues)):
            self.queues[i].min_arrival = args.average_arrival[i]
            self.queues[i].max_arrival = args.average_arrival[i+1]
            self.queues[i].min_service = args.average_service[i]
            self.queues[i].max_service = args.average_service[i+1]
            self.queues[i].number_servers = args.number_servers[i]
            self.queues[i].capacity = args.capacity[i]
            self.queues[i].times = [0] * self.queues[i].capacity
            self.queues[i].weights = [0] * args.number_of_queues
            for j in range(args.number_of_queues):
                self.queues[i].weights[j] = args.weights[k]
                k += 1



def main():
    simulation = QueueSimulator(666)

    for i in range(len(simulation.queues)):
        print('Queue {}'.format(i+1))
        print(' Times: {}'.format(simulation.queues[i].times))
        print(' loss: {}'.format(simulation.queues[i].loss))
        print()

    # queues = [QueueSimulator(10), QueueSimulator(209), QueueSimulator(666), QueueSimulator(5024),
    #           QueueSimulator(9999)]

    # i = 1
    # for queue in queues:
    #     print('Iteration: {}'.format(i))
    #     print(' Queue 1 times: {}'.format(queue.queue1.times))
    #     print(' loss queue 1: {}'.format(queue.queue1.loss))
    #     print()
    #     print(' Queue 2 times: {}'.format(queue.queue2.times))
    #     print(' loss queue 2: {}'.format(queue.queue2.loss))
    #     print()
    #     print(' Total time: {}'.format(round(queue.global_time, 4)))
    #     print('=' * 50)
    #     i += 1

    # average_times = [0] * (queues[0].queue1.capacity + 1)
    # for i in range(len(average_times)):
    #     for queue in queues:
    #         average_times[i] += queue.queue1.times[i]
    #         average_times[i] = round((average_times[i] / len(queues)), 4)

    # average_times2 = [0] * (queues[0].queue2.capacity + 1)
    # for i in range(len(average_times2)):
    #     for queue in queues:
    #         average_times2[i] += queue.queue2.times[i]
    #         average_times2[i] = round((average_times2[i] / len(queues)), 4)

    # print('Average time queue 1: {}'.format(average_times))
    # print('Average time queue 2: {}'.format(average_times2))
    # print('Average total time: {}'.format(round(sum(average_times), 4)))


if __name__ == '__main__':
    main()
