import secrets
import logging

from .runpipe import RunPipe
from ..pipelines.customimputation import imps
from ..pipelines.customclf import clfs
from ..pipelines.customrsp import rsps
from ..pipelines.customhbd import hbds
from ..pipelines.customautoml import automls
from ..components.hybrids import RunAutoSmote
from ..processing.utils import Result
from ..processing.selectiontree import BinaryTree
from ..components.model_filters import ModelFiltering


class AutoImblearn:
    """ The core class that defines how to search the optimal pipeline given a dataset
    Parameters
    ----------
    run_pipe : RunPipe class
        The helper class that has two functions:
            1) handles loading, splitting the data
            2) run the pipelines and get the results

    metric : The evaluation metric defined by user to use during training and final evaluation

    Attributes
    ----------
    resamplers : The list of re-samplers available to choose from

    classifiers : The list of classifiers available to choose from

    hybrids : The list of hybrid re-sampler and classifier methods available to choose from

    imputers : The list of imputers available to choose from

    automls : The list of AutoMLs available to choose from

    run_pipe : RunPipe class

    metric : Evaluation metric
    """
    def __init__(self, run_pipe: RunPipe, metric):
        self.resamplers = list(rsps.keys())
        self.classifiers = list(clfs.keys())
        self.hybrids = list(hbds.keys())
        self.automls = list(automls.keys())
        self.imputers = imps
        self.run_pipe = run_pipe
        self.metric = metric
        self.local_best_pipes = BinaryTree()

    def _train_automl(self, pipeline):
        """ Train the selected automl model """
        if len(pipeline) != 1:
            raise ValueError("Pipeline {} length is not correct, not an automl model")
        # TODO test this function
        result = self.run_pipe.fit_automl(pipeline)
        return result

    def _train_hybird(self, pipeline, args=None, train_ratio=1.0):
        """ Train the pipeline with hybrid resampling method """
        if len(pipeline) != 2:
            raise ValueError("Pipeline {} length is not correct, not a hybrid method pipeline")
        result = self.run_pipe.fit_hybrid(pipeline)
        return result

    def _train_regular(self, pipeline):
        """ Train the pipeline with regular (imputer, resampler, classifier) pipeline """
        if len(pipeline) != 3:
            raise ValueError("Pipeline {} length is not correct, not a regular method pipeline")
        result = self.run_pipe.fit(pipeline)
        return result

    def _init_result_tree(self, result_tree: BinaryTree):
        imp = secrets.choice(self.imputers)
        result_tree.insert(imp, -1, "imp", "root")

        rsp = secrets.choice(self.resamplers)
        result_tree.insert(rsp, -1, "rsp", "imp")

        clf = secrets.choice(self.classifiers)
        result_tree.insert(clf, -1, "clf", "rsp")

        hbd = secrets.choice(self.hybrids)
        result_tree.insert(hbd, -1, "hbd", "imp")

        automl = secrets.choice(self.automls)
        result_tree.insert(automl, -1, "automl", "root")

        # result_tree.print_tree()

    def _compute_current_pipe(self, result_tree: BinaryTree):
        """ Select a path from 3 different pipe types """
        pool = ["automl", "hbd", "clf"]
        pipe_type = secrets.choice(pool)
        pipe = result_tree.build_pipe(pipe_type)
        result_tree.replace(pipe_type, 0, pipe[-1])


        self.model_filtering(topn=3)

    def model_filtering(self, topn=3):
        # Get dataset description
        dp = self.run_pipe.dataloader.get_data_description(self.run_pipe.args.dataset)

        # Get model description TODO

        # Filter models
        model_filter = ModelFiltering(dp, self.run_pipe.dataloader.get_data_folder())
        # TODO make this work
        # filtered_models = model_filter.get_topn()
        # print(filtered_models)

        imputers = model_filter.get_topn("imputer")
        self.imputers = [imputer for imputer in imputers if imputer in self.imputers]

        resamplers = model_filter.get_topn("resampler")
        self.resamplers = [resampler for resampler in resamplers if resampler in self.resamplers]

        classifiers = model_filter.get_topn("classifier")
        self.classifiers = [classifier for classifier in classifiers if classifier in self.classifiers]


    def exhaustive_search(self, checked=None, train_ratio=1.0):
        saver = Result(train_ratio, self.metric)
        saver.load_saved_result()

        for imp in self.imputers:
            for resampler in self.resamplers:
                for classifier in self.classifiers:
                    pipe = [imp, resampler, classifier]
                    print(pipe)
                    if is_checked(pipe, checked):
                        tmp = checked[imp][resampler][classifier]
                    else:
                        if saver.is_in(pipe):
                            tmp = saver.get(pipe)
                        else:
                            try:
                                if resampler == "autosmote":
                                    run_autosmote = RunAutoSmote()
                                    tmp = run_autosmote.fit(clf=classifier, imp=imp, metric=self.metric, train_ratio=train_ratio)
                                else:
                                    tmp = self.run_pipe.fit(pipe)
                            except Exception as e:
                                raise e
                                tmp = 0

                            saver.append(pipe, tmp)
                        checked[imp][resampler][classifier] = tmp
                    print("Current pipe: {}, result: {}".format(pipe, tmp))


    def find_best(self, checked=None, train_ratio=1.0):
        # saver = Result(train_ratio, self.metric, self.run_pipe.args.dataset)
        saver = self.run_pipe.saver
        saver.load_saved_result()

        result_tree = BinaryTree()
        self._init_result_tree(result_tree)
        self._compute_current_pipe(result_tree)
        current_pipe = result_tree.best_pipe()
        # print(current_pipe)
        # result_tree.print_tree()

        counter = 0
        # TODO test saving result , 1) add auto-sklearn to automls (using flask rest API)
        #                                from flask import Flask, jsonify
        best_pipe = []
        best_score = 0
        final_result = set([])

        def update_best_pipe(tmp_pipe, result):
            nonlocal best_pipe, best_score, current_pipe
            if result > best_score:
                best_pipe = list(tmp_pipe)
                best_score = result
            if result_tree.update_pipe(tmp_pipe, result):
                current_pipe = result_tree.best_pipe()
            logging.info(f"This is the best result so far: {best_score} {best_pipe}, This is the current result: {result}, {tmp_pipe}")

        def train_and_update(tmp_pipe):
            nonlocal counter
            if saver.is_in(tmp_pipe):
                result = saver.get(tmp_pipe)
            else:
                if len(tmp_pipe) == 2:
                    result = self._train_hybird(tmp_pipe)
                elif len(tmp_pipe) == 3:
                    result = self._train_regular(tmp_pipe)
                else:
                    result = self._train_automl(tmp_pipe)
                saver.append(tmp_pipe, result)
                counter += 1
            update_best_pipe(tmp_pipe, result)
            return result


        while True:
            # Brute force method
            # Step 1: Choose imputater or other automl
            # for model in self.imputers + self.automls:
            for model in self.imputers:
                if model in self.imputers:
                    # Regular or Hybrid method
                    tmp_pipe = result_tree.sub_best_pipe(node_type="imp")
                    if len(tmp_pipe) == 2:
                        tmp_pipe = [model] + tmp_pipe[1:]

                        result = train_and_update(tmp_pipe)

                    elif len(tmp_pipe) == 3:
                        tmp_pipe = [model] + tmp_pipe[1:]
                        result = train_and_update(tmp_pipe)
                    else:
                        raise ValueError(
                            "Pipeline length of {} is not compatible with AutoImblearn".format(current_pipe))

                else:
                    # AutoML method
                    tmp_pipe = [model]
                    result = train_and_update(tmp_pipe)


                # print("This is the best result so far: ", best_score, best_pipe, "This is the current result: ", result, tmp_pipe)
                # print(result, best_score)
                if result > best_score:
                    best_pipe = list(tmp_pipe)
                    best_score = result

            if len(current_pipe) != 1:
                # Step 2: Choose resampler
                for model in self.resamplers + self.hybrids:
                    if model in self.resamplers:
                        sub_pipe = result_tree.sub_best_pipe("clf")
                        tmp_pipe = [current_pipe[0], model] + sub_pipe

                        result = train_and_update(tmp_pipe)
                    else:
                        # Hybrid method
                        tmp_pipe = [current_pipe[0], model]
                        result = train_and_update(tmp_pipe)

                    # print("This is the best result so far: ", best_score, best_pipe, "This is the current result: ", result, tmp_pipe)
                    if result > best_score:
                        best_pipe = list(tmp_pipe)
                        best_score = result

            if len(current_pipe) == 3:
                # Step 3: Choose classifier
                for model in self.classifiers:
                    tmp_pipe = current_pipe[:2] + [model]
                    result = train_and_update(tmp_pipe)

                    # print("This is the best result so far: ", best_score, best_pipe, "This is the current result: ", result, tmp_pipe)
                    if result > best_score:
                        best_pipe = list(tmp_pipe)
                        best_score = result

            if set(best_pipe) == set(final_result):
                break
            else:
                final_result = list(best_pipe)

        best_pipe = result_tree.best_pipe()
        result_tree.print_tree()
        return best_pipe, counter, best_score

    def run_best(self, pipeline=None):
        # Re-run the best pipeline found with 100% of data
        # saver = Result(1.0, self.metric, self.run_pipe.args.dataset)
        saver = self.run_pipe.saver
        saver.load_saved_result()
        if saver.is_in(pipeline):
            result = saver.get(pipeline)
        else:
            if len(pipeline) == 1:
                result = self._train_automl(pipeline)
            elif len(pipeline) == 2:
                result = self._train_hybird(pipeline, args, 1.0)
            elif len(pipeline) == 3:
                result = self._train_regular(pipeline)
            else:
                raise Exception("Pipeline {} is not in the correct length".format(pipeline))

        return result

    def count_pipe(self, pipeline=None):
        # Find the optimal and count how many pipelines to check
        counters = []
        for _ in range(100):
            checked = []
            final, count, best_score = self.find_best(checked)
            while final != set(pipeline):
                final, count, best_score = self.find_best(checked)
            counters.append(count)
        return counters


if __name__ == "__main__":
    class Args:
        def __init__(self):
            self.train_ratio=1.0
            self.n_splits = 10
            self.repeat = 0
            self.dataset = "test"
            self.metric = "auroc"
    args = Args()
    run_pipe = RunPipe(args)
    autoimb = AutoImblearn(run_pipe, metric=args.metric)
    tmp_tree = BinaryTree()
    autoimb._init_result_tree(tmp_tree)
    tmp_tree.print_tree()

    autoimb._compute_current_pipe(tmp_tree)

    tmp_pipe = tmp_tree.best_pipe()
    # print(tmp_pipe)
    # tmp_tree.print_tree()
    result = tmp_tree.build_pipe("clf")
    print(result)

    tmp_tree.update_pipe(["ii", "smote", "mlp"], 2)
    tmp_tree.update_pipe(["ii", "under", "svm"], 1)
    tmp_tree.print_tree()

