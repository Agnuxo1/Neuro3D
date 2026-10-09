import unittest
import numpy as np
from Blender.blender_lab.classifier_comparison_v1 import encode_real_features,design_matrix,softmax_objective,fit_baseline,baseline_scores,classification_metrics,paired_comparison


class ComparisonControls(unittest.TestCase):
    def test_train_only_scaler_and_unclipped_holdout(self):
        raw=np.asarray([[0,1,2,3],[1,2,3,4],[100,200,300,400]],dtype=float)
        sources=['c2','r1','c1','r0','c0']
        x,metadata=encode_real_features(raw,[0,1],sources)
        self.assertEqual(metadata['hi'],[1,2,3,4]);self.assertEqual(metadata['fit_rows'],[0,1])
        self.assertAlmostEqual(x[2,3]/x[2,0],100);np.testing.assert_allclose(np.sum(x*x,axis=1),1)
        raw[2]*=10;_,new=encode_real_features(raw,[0,1],sources);self.assertEqual(new,metadata)

    def test_convex_gradient_and_fit_independent_fd(self):
        rng=np.random.default_rng(118);x=rng.normal(size=(60,5));y=np.repeat(np.arange(3),20)
        x[np.arange(60),y]+=3
        for kind in ('linear','quadratic'):
            z=design_matrix(x,kind);w=rng.normal(size=3*z.shape[1])*.1
            loss,gradient=softmax_objective(w,z,y,.001)
            for j in range(len(w)):
                d=np.eye(len(w))[j]*1e-6
                numerical=(softmax_objective(w+d,z,y,.001)[0]-softmax_objective(w-d,z,y,.001)[0])/2e-6
                self.assertLess(abs(numerical-gradient[j]),1e-8)
            model=fit_baseline(x,y,kind,{'l2':.001,'maxiter':2000,'gtol':1e-8,'ftol':1e-12,'maximum_gradient_abs':1e-5})
            self.assertGreater(np.mean(np.argmax(baseline_scores(model,x),axis=1)==y),.9)

    def test_quadratic_map_and_paired_counts(self):
        x=np.array([[1,2,3,4,5]],dtype=float);z=design_matrix(x,'quadratic')
        self.assertEqual(z.shape,(1,15));self.assertEqual(z[0,1],2)
        metrics=classification_metrics([0,1,2,1],[0,1,1,2]);self.assertEqual(metrics['correct'],2)
        report=paired_comparison([0,1,2,1],[0,2,1,1],np.array([0,1,1,2]))
        self.assertEqual(report['own_only_correct'],1);self.assertEqual(report['baseline_only_correct'],1)
        self.assertEqual(report['mcnemar_exact_two_sided_p'],1)


if __name__=='__main__':unittest.main()
